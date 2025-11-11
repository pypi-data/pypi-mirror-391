import copy, os, json, uuid
from loguru import logger
from pyspark.sql import SparkSession
from pyspark.sql.types import Row
from pyspark.sql.functions import monotonically_increasing_id
from data_engine.core.base import BaseProcessor
from data_engine.define import OpType
from data_engine.utils.log_utils import default_serializer

# from typing import Any
# import numpy as np


# def wrap(func, params):
#     """
#     执行函数并根据 path 保存结果（仅支持 NFS）
#     """
#     path = params.pop("path", None)
#     if path:
#         os.makedirs(path, exist_ok=True)
#         unique_id = uuid.uuid4()
#         path = os.path.join(path, f"{unique_id}.json")
#     result = func(**params) if callable(func) else func
#     if path and not hasattr(result, "toDF"):  # RDD action 返回非 DataFrame
#         with open(path, "w") as f:
#             try:
#                 json.dump(result, f, ensure_ascii=False, default=default_serializer)
#             except Exception as e:
#                 logger.error(f'在tool.wrap写入异常data:{result},原因：{str(e)}')
#                 raise e

#     return result

# class BaseSparkTool(BaseProcessor):
#     op_type: str = OpType.TOOL

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self._engine_config = kwargs.get("_engine_config", {}) or {}
#         self.kwargs = kwargs.get("kwargs", {}) or {}
#         self.params = {}

#         workspace = self._engine_config.get("workspace")
#         skip_keys = ("s3_conf",)

#         for k, v in self.kwargs.items():
#             if k.startswith("_engine") or k in skip_keys:
#                 continue
#             if k == "path":
#                 v = v or ""
#                 v = v.strip()
#                 if not v:
#                     raise RuntimeError("path not null")
#                 if "s3_conf" not in self.kwargs and not v.startswith("/"):
#                     v = os.path.join(workspace, v)
#             self.params[k] = copy.deepcopy(v)


# class SparkMap(BaseSparkTool):
#     """
#     映射算子
#     fn: 映射函数#callable#应用于每条数据
#     """

#     def run(self, rdd):
#         return rdd.map(self.params["fn"])


# class SparkFilter(BaseSparkTool):
#     """
#     过滤算子
#     fn: 过滤函数#callable#返回 True 的保留，False 的丢弃
#     """

#     def run(self, rdd):
#         return rdd.filter(self.params["fn"])


# class SparkFlatMap(BaseSparkTool):
#     """
#     扁平映射算子
#     fn: 映射函数#callable#每个元素映射为迭代器，最终展开
#     """

#     def run(self, rdd):
#         return rdd.flatMap(self.params["fn"])


# class SparkReduceByKey(BaseSparkTool):
#     """
#     按 key 聚合
#     fn: 聚合函数#callable#用于聚合相同 key 的 value
#     numPartitions: 分区数量#int#结果 RDD 分区数
#     """

#     def run(self, rdd):
#         return rdd.reduceByKey(**self.params)


# class SparkJoin(BaseSparkTool):
#     """
#     内连接
#     other: 另一个 RDD#RDD#需要 join 的 RDD
#     numPartitions: 分区数量#int#结果分区数
#     """

#     def run(self, rdd):
#         return rdd.join(**self.params)


# class SparkCount(BaseSparkTool):
#     """
#     统计 RDD 行数
#     """

#     def run(self, rdd):
#         return wrap(rdd.count, self.params)


# class SparkTake(BaseSparkTool):
#     """
#     获取前 n 行
#     num: 返回的行数#[1, 正无穷]#最多返回的行数
#     """

#     def run(self, rdd):
#         num = self.params.get("num", 20)
#         result = rdd.take(num)
#         return wrap(result, self.params)


# class SparkCollect(BaseSparkTool):
#     """
#     获取所有数据
#     """

#     def run(self, rdd):
#         result = rdd.collect()
#         return wrap(result, self.params)


# class SparkDistinct(BaseSparkTool):
#     """
#     去重
#     numPartitions: 分区数量#int#结果 RDD 分区数
#     """

#     def run(self, rdd):
#         return rdd.distinct(**self.params)


# class SparkUnion(BaseSparkTool):
#     """
#     合并 RDD
#     other: 另一个 RDD#RDD#需要合并的 RDD
#     """

#     def run(self, rdd):
#         return rdd.union(self.params["other"])


# class SparkSortBy(BaseSparkTool):
#     """
#     排序
#     keyfunc: 排序函数#callable#用于提取排序键
#     ascending: 是否升序#[True, False]#默认 True
#     numPartitions: 分区数量#int#结果 RDD 分区数
#     """

#     def run(self, rdd):
#         return rdd.sortBy(**self.params)


# class SparkSample(BaseSparkTool):
#     """
#     随机抽样
#     withReplacement: 是否放回#[True, False]#默认 False
#     fraction: 抽样比例#[0,1]#要抽取的比例
#     seed: 随机种子#int#用于随机数生成
#     """

#     def run(self, rdd):
#         return rdd.sample(**self.params)


# class SparkAddId(BaseSparkTool):
#     """
#     为无唯一标识的数据集添加自增ID，便于后续追踪或关联操作。如col: id
#     """
#     def __init__(self, col='id', **kwargs):
#         super().__init__(**kwargs)
#         self.col = col


#     def run(self, rdd):
#         rdd = rdd.zipWithIndex() \
#         .map(
#             lambda x: {**{k: v for k, v in x[0].items() if k != 'id'},
#                         self.col: x[1] + 1}
#         )
#         return rdd


import copy, os, json, uuid
from pyspark.sql import DataFrame
from data_engine.core.base import BaseProcessor
from data_engine.define import OpType


def wrap_spark(func, params):
    """封装 Spark 算子结果保存逻辑"""
    path = params.pop("path", "result")
    print(f"---func :{func}")
    result = func(**params) if callable(func) else func

    if path:
        os.makedirs(path, exist_ok=True)
        unique_id = uuid.uuid4()
        path_file = os.path.join(path, f"{unique_id}.json")
        if isinstance(result, DataFrame):
            # print(f'wrap_spark DataFrame:{path}')
            result.write.mode("overwrite").json(path)
        else:
            with open(path_file, "w") as f:
                try:
                    result = [
                        item.asDict() if isinstance(item, Row) else item
                        for item in result
                    ]
                    json.dump(result, f, ensure_ascii=False, default=default_serializer)
                except Exception as e:
                    logger.error(
                        f"在tool.wrap_spark写入异常data:{path_file},原因：{str(e)}"
                    )
                    raise e

    return result


class BaseSparkTool(BaseProcessor):
    op_type: str = OpType.TOOL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.get("kwargs", {}) or {}
        self.params = {}

        workspace = self._engine_config.get("workspace")
        for k, v in self.kwargs.items():
            if k.startswith("_engine"):
                continue
            if k == "path" and not v.startswith("/"):
                v = os.path.join(workspace, v)
            self.params[k] = copy.deepcopy(v)


# ---------------- 算子工具类 ----------------
class SparkFromItems(BaseSparkTool):
    """
    从 Python 列表创建 RDD
    items: 数据列表 #list# 要并行化的 Python 对象列表
    numSlices: 分区数 #[1, 正无穷]# 分片数，默认由 Spark 自动推断dataframe
    """

    def run(self, data):
        from data_engine.core.factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("spark")
        sc = executor.spark.sparkContext
        items = self.params["items"]
        numSlices = self.params.get("numSlices")

        if numSlices and isinstance(numSlices, int) and numSlices > 0:
            rdd = sc.parallelize(items, numSlices)
        else:
            rdd = sc.parallelize(items)

        from data_engine.core.factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("spark")
        # 转换为DataFrame时处理可能的类型问题
        try:
            df = executor.spark.createDataFrame(rdd)
        except Exception as e:
            print(f"读取{items}失败: {str(e)}")
            raise e

        # df.show(truncate=False)
        return df
        # return sc.parallelize(items, numSlices) if numSlices else sc.parallelize(items)


class SparkToolLimit(BaseSparkTool):
    """截断前 limit 行
    先通过 limit(n) 筛选前 n 行，再拉取到 Driver（等价于 take(n)

    """

    def run(self, dataset: DataFrame):
        num = self.params.get("num", 10)
        return wrap_spark(dataset.limit(num), self.params)
        # return dataset.limit(limit)


class SparkToolTake(BaseSparkTool):
    """
    拉取前 n 行数据到 Driver，返回 [Row, ...] 列表
    返回 Row 对象的列表（拉取到 Driver节点的本地数据），适用于查看少量样本
    """

    def run(self, dataset: DataFrame):
        num = self.params.get("num", 10)

        return wrap_spark(dataset.take(num), self.params)


class SparkToolCollect(BaseSparkTool):
    """
    全量拉取所有数据到 Driver，返回 [Row, ...] 列表
    全量拉取到 Driver 会导致内存溢出（OOM）
    """

    def run(self, dataset: DataFrame):
        num = self.params.get("num", 10)
        return wrap_spark(dataset.collect(), self.params)


class SparkToolSelectColumns(BaseSparkTool):
    """选择指定列"""

    def run(self, dataset: DataFrame):
        cols = self.params["cols"]
        return dataset.select(*cols)


class SparkToolDropColumns(BaseSparkTool):
    """删除指定列"""

    def run(self, dataset: DataFrame):
        cols = self.params["cols"]
        return dataset.drop(*cols)


class SparkToolFilter(BaseSparkTool):
    """过滤数据"""

    def run(self, dataset: DataFrame):
        expr = self.params.get("expr")
        if expr:
            return dataset.filter(expr)
        fn = self.params.get("fn")
        if fn:
            return dataset.filter(fn)
        return dataset


class SparkToolGroupby(BaseSparkTool):
    """分组聚合"""

    def run(self, dataset: DataFrame):
        by = self.params["by"]
        agg = self.params["agg"]  # dict 形式 {col: "sum"/"max"/"count"}
        return dataset.groupBy(*by).agg(agg)


class SparkToolJoin(BaseSparkTool):
    """数据集连接"""

    def run(self, dataset: DataFrame):
        other = self.params["other"]
        on = self.params.get("on")
        how = self.params.get("how", "inner")
        return dataset.join(other, on=on, how=how)


class SparkToolSort(BaseSparkTool):
    """排序"""

    def run(self, dataset: DataFrame):
        key = self.params["key"]
        descending = self.params.get("descending", False)
        if isinstance(key, str):
            key = [key]
        return dataset.orderBy(
            *[dataset[k].desc() if descending else dataset[k].asc() for k in key]
        )


class SparkToolCount(BaseSparkTool):
    """统计行数"""

    def run(self, dataset: DataFrame):
        return wrap_spark([{"count": dataset.count()}], self.params)


class SparkToolDistinct(BaseSparkTool):
    """去重"""

    def run(self, dataset: DataFrame):
        return dataset.distinct()


class SparkToolSample(BaseSparkTool):
    """随机采样"""

    def run(self, dataset: DataFrame):
        fraction = self.params.get("fraction", 0.1)
        seed = self.params.get("seed", None)
        return dataset.sample(fraction=fraction, seed=seed)


class SparkToolAddId(BaseSparkTool):
    """
    为无唯一标识的数据集添加递增但不连续的id列ID，便于后续追踪或关联操作。如col: id
    分区内连续递增
    """

    def __init__(self, col="id", **kwargs):
        super().__init__(**kwargs)
        self.col = col

    def run(self, dataset: DataFrame):
        df = dataset
        # 检查ID列是否已存在
        if self.col not in dataset.columns:
            # 添加自增ID列，使用Spark分布式唯一递增ID生成函数
            df = dataset.withColumn(self.col, monotonically_increasing_id())

        return df


class SparkToolRenameColumns(BaseSparkTool):
    """
    重命名数据集中的列
    names: 列名映射或列表#dict or list#用于列重命名的映射，
        如{"content": "new_content","id": "new_id"}
    """

    def run(self, df: DataFrame):
        # 定义要改的列名映射
        # 循环调用withColumnRenamed，改完后其他列会自动保留
        recolums = self.params["names"]

        for old_col, new_col in recolums.items():
            df = df.withColumnRenamed(old_col, new_col)
        return df
