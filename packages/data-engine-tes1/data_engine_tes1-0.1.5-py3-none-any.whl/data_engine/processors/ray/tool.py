import copy, ray, ast, os, json, uuid
from data_engine.core.base import BaseProcessor
from data_engine.define import OpType
from data_engine.utils.name_provider import NameProvider
from data_engine.utils.model_utils import get_model_path


def _create_lambda(func_str: str, func_name: str = "process"):
    tree = ast.parse(func_str)
    func_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    code_obj = compile(tree, filename="<string>", mode="exec")
    namespace = {}
    exec(code_obj, namespace)
    if len(func_defs) == 1:
        func_name = func_defs[0].name
    else:
        func_name = func_name

    return namespace.get(func_name) or namespace.get("main")


def wrap(func, params):
    path = params.pop("path", "result")
    if path:
        os.makedirs(path, exist_ok=True)
        unique_id = uuid.uuid4()
        path = os.path.join(path, f"{unique_id}.json")
    result = func(**params)
    if path and not isinstance(result, ray.data.Dataset):
        with open(path, "w") as f:
            json.dump(result, f, ensure_ascii=False)
    return result


class BaseRayTool(BaseProcessor):
    op_type: str = OpType.TOOL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.get("kwargs", {}) or {}
        self.params = {}

        skip_keys = ("s3_conf",)
        workspace = self._engine_config.get("workspace")

        for k, v in self.kwargs.items():
            if k.startswith("_engine") or k in skip_keys:
                continue
            if k == "fn":
                self.params[k] = _create_lambda(v)
                continue
            if k == "path":
                v = v or ""
                v = v.strip()
                if "s3_conf" not in self.kwargs and not v.startswith("/"):
                    v = os.path.join(workspace, v)

            self.params[k] = copy.deepcopy(v)


class ToolLimit(BaseRayTool):
    """
    截断数据集
    将数据集截断为前 limit 行
    """

    def __init__(self, **kwargs):
        """
        初始化方法
        limit: 截断行数#[1, 正无穷]#数据集的大小要截断。
        """
        super().__init__(**kwargs)

    def run(self, dataset):
        self.params["limit"] = self.params.get("limit", 20)
        return dataset.limit(**self.params)


class ToolJoin(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.join(**self.params)


class ToolCount(BaseRayTool):
    """
    统计数据集的行数
    """

    def __init__(self, **kwargs):
        """
        初始化方法
        无参数
        """
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.count, self.params)


class ToolRepartition(BaseRayTool):
    """
    对数据集重新分区
    将数据集重新分区为指定数量的 block

    num_blocks: 分区数量#[1, 正无穷]#最终的数据块数量
    target_num_rows_per_block: 每个 block 目标行数#[1, 正无穷]#控制每个 block 大小（实验性）
    shuffle: 是否启用随机打散#[True, False]#是否在重分区时进行数据打散
    # keys: 分区键列名列表#list#基于键的哈希分区（需配置上下文）
    sort: 是否对每个 block 排序#[True, False]#是否对 block 排序，默认升序
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.repartition(**self.params)


class ToolTake(BaseRayTool):
    """
    获取数据集前若干行
    limit: 最大返回行数#[1, 正无穷]#最多返回的行数
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        limit = self.params.pop("limit", 20)
        dataset = dataset.limit(limit=limit)
        if "path" in self.params:
            ext = NameProvider("jsonl")
            self.params["filename_provider"] = ext
            result = dataset.write_json(force_ascii=False, **self.params)
        else:
            result = dataset.take_all()
        return result


class ToolTakeAll(BaseRayTool):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        if "path" in self.params:
            result = dataset.write_json(force_ascii=False, **self.params)
        else:
            result = dataset.take_all()
        return result


class ToolRenameColumns(BaseRayTool):
    """
    重命名数据集中的列
    names: 列名映射或列表#dict or list#用于列重命名的映射或新列名列表
    concurrency: 并发数量#[1, 正无穷]#最大并发 worker 数量
    ray_remote_args: Ray 远程执行参数#dict#用于资源指定，如 num_gpus 等
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.rename_columns(**self.params)


class ToolSelectColumns(BaseRayTool):
    """
    选择数据集中的列
    cols: 需要选择的列名列表#list#列名必须唯一且存在于 schema 中
    concurrency: 并发数量#[1, 正无穷]#最大并发 worker 数量
    ray_remote_args: Ray 远程执行参数#dict#用于资源指定，如 num_gpus 等
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.select_columns(**self.params)


class ToolDropColumns(BaseRayTool):
    """
    删除数据集中的列
    cols: 需要删除的列名列表#list#列名必须唯一且存在于 schema 中
    concurrency: 并发数量#[1, 正无穷]#最大并发 worker 数量
    ray_remote_args: Ray 远程执行参数#dict#用于资源指定，如 num_gpus 等
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.drop_columns(**self.params)


class ToolMax(BaseRayTool):
    """
    计算某列的最大值
    on: 目标列名或列名列表#str or list#需要聚合的列名
    ignore_nulls: 是否忽略空值#[True, False]#是否跳过空值（None、NaN、NaT）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.max, self.params)


class ToolMin(BaseRayTool):
    """
    计算某列的最小值
    on: 目标列名或列名列表#str or list#需要聚合的列名
    ignore_nulls: 是否忽略空值#[True, False]#是否跳过空值（None、NaN、NaT）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.min, self.params)


class ToolMean(BaseRayTool):
    """
    计算某列的均值
    on: 目标列名或列名列表#str or list#需要聚合的列名
    ignore_nulls: 是否忽略空值#[True, False]#是否跳过空值（None、NaN、NaT）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.mean, self.params)


class ToolStd(BaseRayTool):
    """
    计算某列标准差
    on: 目标列名或列名列表#str or list#需要聚合的列名
    ignore_nulls: 是否忽略空值#[True, False]#是否跳过空值（None、NaN、NaT）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.std, self.params)


class ToolSum(BaseRayTool):
    """
    计算某列的总和
    on: 目标列名或列名列表#str or list#需要聚合的列名
    ignore_nulls: 是否忽略空值#[True, False]#是否跳过空值（None、NaN、NaT）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.sum, self.params)


class ToolUnique(BaseRayTool):
    """
    列出指定列中的所有唯一元素（即去重后的值）
    on: 目标列名或列名列表#str or list#需要聚合的列名
    ignore_nulls: 是否忽略空值#[True, False]#是否跳过空值（None、NaN、NaT）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.unique, self.params)


class ToolColumns(BaseRayTool):
    """
    获取数据集的所有列名
    fetch_if_missing: 是否强制同步获取列名#[True, False]#若为 True 且未知 schema，则同步获取
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return wrap(dataset.columns, self.params)


class ToolSort(BaseRayTool):
    """
    对数据集进行排序
    key: 排序键或键列表#str or list#用于排序的列
    descending: 是否降序#[True, False] or list#控制升序或降序
    boundaries: 分区边界#list#指定边界进行分区排序（仅支持数值列）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.sort(**self.params)


class ToolRandomSample(BaseRayTool):
    """
    随机抽样数据集行
    fraction: 抽样比例#[0,1]#要抽取的比例
    seed: 随机种子#int#用于随机数生成器的种子设置
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.random_sample(**self.params)


class ToolRandomShuffle(BaseRayTool):
    """
    随机洗牌此数据集。
    seed: 随机种子#int#用于随机数生成器的种子设置
    num_blocks: 分区数量#[1, 正无穷]#最终的数据块数量
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.random_shuffle(**self.params)


class ToolFilter(BaseRayTool):

    def __init__(self, **kwargs):
        """
        数据过滤
        fn – 要应用于每一行的谓词函数，或者一个可实例化为此类可调用对象的类类型。
        expr – 一个表达式字符串，必须是有效的 Python 表达式，会被转换为 pyarrow.dataset.Expression 类型。
        fn_kwargs – 传递给 fn 的关键字参数。这些参数是传递给底层 Ray 任务的顶层参数。
        """

        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.filter(**self.params)


class ToolGroupby(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.groupby(**self.params)


class ToolMapGroups(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.map_groups(**self.params)


class ToolMapBatchs(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.map_batches(**self.params)


class ToolMap(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.map(**self.params)


class ToolFlatMap(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.flat_map(**self.params)


class ToolAddColumn(BaseRayTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, dataset):
        return dataset.add_column(**self.params)


class ToolStats(BaseRayTool):
    def run(self, dataset):
        return dataset.materialize().stats()


class ToolAddId(BaseRayTool):
    def __init__(self, col=None, **kwargs):
        super().__init__(**kwargs)
        self.col = col

    def run(self, dataset):
        n = dataset.count()
        id_ds = ray.data.range(n)
        if self.col and self.col != "id":
            id_ds = id_ds.rename_columns({"id": self.col})
        ds_with_id = dataset.zip(id_ds)
        return ds_with_id


class ToolVllmEngine(BaseRayTool):
    def __init__(self, config: dict, preprocess=None, postprocess=None, **kwargs):
        super().__init__(**kwargs)
        from ray.data.llm import vLLMEngineProcessorConfig, build_llm_processor

        if preprocess:
            preprocess = _create_lambda(preprocess)
        else:
            preprocess = lambda row: dict(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful and concise assistant.",
                    },
                    {"role": "user", "content": row["prompt"]},
                ],
                sampling_params=dict(repetition_penalty=1.2, max_tokens=2048),
            )
        if postprocess:
            postprocess = _create_lambda(postprocess)
        config["model_source"] = get_model_path(config["model_source"])
        self.processor = build_llm_processor(
            vLLMEngineProcessorConfig(**config),
            preprocess=preprocess,
            postprocess=postprocess,
        )

    def run(self, dataset):
        return self.processor(dataset)


class ToolHttpRequest(BaseRayTool):
    def __init__(self, config: dict, preprocess=None, postprocess=None, **kwargs):
        super().__init__(**kwargs)
        from ray.data.llm import HttpRequestProcessorConfig, build_llm_processor

        if preprocess:
            preprocess = _create_lambda(preprocess)
        else:
            preprocess = lambda row: dict(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful and concise assistant.",
                    },
                    {"role": "user", "content": row["prompt"]},
                ],
                sampling_params=dict(repetition_penalty=1.2, max_tokens=2048),
            )
        if postprocess:
            postprocess = _create_lambda(postprocess)
        self.processor = build_llm_processor(
            HttpRequestProcessorConfig(**config),
            preprocess=preprocess,
            postprocess=postprocess,
        )

    def run(self, dataset):
        return self.processor(dataset)
