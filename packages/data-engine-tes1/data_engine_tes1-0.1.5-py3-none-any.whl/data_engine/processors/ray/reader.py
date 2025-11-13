import ray, copy, s3fs
from data_engine.core.base import BaseReader, BaseS3


class RayReaderJsonline(BaseReader, BaseS3):
    """
    从 JSON / JSONL 文件创建数据集
    对于 JSON 文件，将整个文件作为一行；对于 JSONL 文件，每行作为一行读取
    """

    def __init__(self, **kwargs):
        """
        初始化方法
        paths: 路径#[字符串或字符串列表]#文件或目录路径，可同时包含多个 JSON 或 JSONL 文件路径
        lines: 按行读取#[bool]#是否以 JSONL 格式读取每行，启用后忽略部分高级参数
        filesystem: 文件系统#[pyarrow 文件系统对象]#用于读取的文件系统，默认根据路径前缀自动识别（如 s3://）
        ray_remote_args: Ray远程参数#[字典]#传递给 ray.remote() 的任务执行参数
        arrow_open_stream_args: 文件读取参数#[字典]#用于打开文件时传给 pyarrow.fs.FileSystem 的参数
        meta_provider: 元数据提供器#[None 或对象]#自定义元数据读取策略，通常不需要设置
        partition_filter: 分区过滤器#[函数]#用于根据路径筛选特定数据分区
        partitioning: 分区描述#[对象]#路径分区方式，默认采用 Hive 风格分区
        include_paths: 包含路径列#[bool]#是否在结果中包含原始文件路径（列名为 path）
        ignore_missing_paths: 忽略不存在路径#[bool]#是否忽略未找到的文件路径
        shuffle: 文件顺序打乱方式#[None 或对象]#读取前是否打乱文件顺序，可设置随机种子
        arrow_json_args: JSON 读取参数#[字典]#传递给 pyarrow.json.read_json 的读取配置
        file_extensions: 文件后缀过滤#[字符串列表]#用于筛选的文件扩展名列表（如 .json, .jsonl）
        concurrency: 并发任务数#[int 或 None]#[1, 正无穷]#最大并发任务数量，默认根据资源动态调整
        override_num_blocks: 块数覆盖#[int 或 None]#[1, 正无穷]#输出数据块数量覆盖，通常不建议手动设置
        """
        super().__init__(**kwargs)

    def run(self, data):
        kwargs = self.params
        result = ray.data.read_json(filesystem=self.fs, **kwargs)
        return result


class RayReaderParquet(BaseReader, BaseS3):
    """
    从 Parquet 文件创建数据集
    """

    def __init__(self, **kwargs):
        """
        初始化方法
        paths: 路径#[字符串或字符串列表]#单个文件路径或目录路径，暂不支持多个目录
        filesystem: 文件系统#[pyarrow 文件系统对象或 None]#用于读取的文件系统，默认根据路径自动识别（如 s3://）
        columns: 列选择#[字符串列表]#只读取指定列，提升性能
        ray_remote_args: Ray远程参数#[字典]#传递给 ray.remote() 的任务执行参数
        tensor_column_schema: 张量列结构#[字典]#指定张量列的名称、数据类型与形状，用于反序列化
        meta_provider: 元数据提供器#[None 或对象]#自定义元数据读取器，通常不需要设置
        partition_filter: 分区过滤器#[函数]#用于选择性读取分区数据
        partitioning: 分区描述#[对象]#路径分区方式，默认为 Hive 风格分区
        shuffle: 文件顺序打乱方式#[None 或对象]#读取前是否打乱文件顺序，可设置随机种子
        arrow_parquet_args: Parquet读取参数#[字典]#传递给 pyarrow 的读取配置
        include_paths: 包含路径列#[bool]#是否在结果中包含原始文件路径（列名为 path）
        file_extensions: 文件后缀过滤#[字符串列表]#用于筛选的文件扩展名（如 .parquet）
        concurrency: 并发任务数#[int 或 None]#[1, 正无穷]#最大并发任务数，默认根据系统资源自动决定
        override_num_blocks: 块数覆盖#[int 或 None]#[1, 正无穷]#输出数据块数量，通常不建议手动设置
        """
        super().__init__(**kwargs)

    def run(self, data):

        kwargs = self.params
        result = ray.data.read_parquet(filesystem=self.fs, **kwargs)
        return result


class RayReaderText(BaseReader, BaseS3):
    """
    从 text 文件创建数据集
    """

    def __init__(self, **kwargs):
        """
        初始化方法
        paths: 路径#[字符串或字符串列表]#单个文件路径或目录路径，暂不支持多个目录
        filesystem: 文件系统#[pyarrow 文件系统对象或 None]#用于读取的文件系统，默认根据路径自动识别（如 s3://）
        columns: 列选择#[字符串列表]#只读取指定列，提升性能
        ray_remote_args: Ray远程参数#[字典]#传递给 ray.remote() 的任务执行参数
        tensor_column_schema: 张量列结构#[字典]#指定张量列的名称、数据类型与形状，用于反序列化
        meta_provider: 元数据提供器#[None 或对象]#自定义元数据读取器，通常不需要设置
        partition_filter: 分区过滤器#[函数]#用于选择性读取分区数据
        partitioning: 分区描述#[对象]#路径分区方式，默认为 Hive 风格分区
        shuffle: 文件顺序打乱方式#[None 或对象]#读取前是否打乱文件顺序，可设置随机种子
        arrow_parquet_args: Parquet读取参数#[字典]#传递给 pyarrow 的读取配置
        include_paths: 包含路径列#[bool]#是否在结果中包含原始文件路径（列名为 path）
        file_extensions: 文件后缀过滤#[字符串列表]#用于筛选的文件扩展名（如 .parquet）
        concurrency: 并发任务数#[int 或 None]#[1, 正无穷]#最大并发任务数，默认根据系统资源自动决定
        override_num_blocks: 块数覆盖#[int 或 None]#[1, 正无穷]#输出数据块数量，通常不建议手动设置
        """
        super().__init__(**kwargs)

    def run(self, data):

        kwargs = self.params
        result = ray.data.read_text(filesystem=self.fs, **kwargs)
        return result


class RayReaderFromItems(BaseReader):
    """
    从本地 Python 对象列表创建数据集
    适用于创建内存中小型数据集，默认列名为 "item"
    """

    def __init__(self, **kwargs):
        """
        初始化方法
        items: 本地对象列表#[列表]#内存中的原始数据对象列表
        override_num_blocks: 块数覆盖#[int 或 None]#[1, 正无穷]#输出数据块数量，通常不建议手动设置
        """
        super().__init__(**kwargs)

    def run(self, data):
        kwargs = self.params
        result = ray.data.from_items(**kwargs)
        return result
