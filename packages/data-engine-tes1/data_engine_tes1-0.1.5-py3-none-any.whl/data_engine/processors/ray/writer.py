import s3fs, os
from data_engine.core.base import BaseConsumer, BaseS3
from data_engine.utils.name_provider import NameProvider


class RayWriterJsonline(BaseConsumer, BaseS3):
    """
    JSON/JSONL 文件写入器
    将数据集写入 JSON 或 JSONL 格式的文件。
    - JSON 文件按整文件写入一行；
    - JSONL 文件按每行写入一行。

    支持路径过滤、分区、并发控制等配置。
    """

    def __init__(self, **kwargs):
        """
        初始化方法

        path: 路径列表#list[str]#单个或多个文件/目录路径，可混合 JSON 与 JSONL 文件
        lines: 行分隔模式#bool#是否启用 JSONL 模式（按行读取/写入）
        filesystem: 文件系统#pyarrow.fs.FileSystem#用于读写文件的文件系统对象（默认根据路径自动推断）
        ray_remote_args: Ray远程参数#dict#传递给 ray.remote() 的参数
        arrow_open_stream_args: 输入流参数#dict#传递给 pyarrow.fs.FileSystem.open_input_file 的参数
        meta_provider: 元信息提供器#Any#用于提供自定义文件元信息（已废弃）
        partition_filter: 分区过滤器#Callable#路径分区过滤函数，默认仅处理 .json/.jsonl 文件
        partitioning: 分区对象#Partitioning#描述路径组织结构（默认支持 Hive 风格分区）
        include_paths: 包含路径列#bool#是否在输出中包含文件路径字段 'path'
        ignore_missing_paths: 忽略缺失路径#bool#为 True 时忽略不存在的路径
        shuffle: 文件随机打乱#None或FileShuffleConfig#可通过配置随机种子打乱文件顺序
        arrow_json_args: JSON读取参数#dict#传递给 pyarrow.json.read_json 的选项
        file_extensions: 文件扩展名#list[str]#用于筛选文件的扩展名列表
        concurrency: 并发任务数#[1, 正无穷]#最大并发 Ray 任务数（默认自动决定）
        override_num_blocks: 块数覆盖#[1, 正无穷]#覆盖读取后数据集的 block 数（一般无需设置）
        """
        super().__init__(**kwargs)

    def run(self, dataset):
        ext_name = self.params.pop("ext_name", "jsonl")
        ext = NameProvider(ext_name)
        self.params["filename_provider"] = ext
        result = dataset.write_json(filesystem=self.fs, **self.params)
        return result


class RayWriterCsv(BaseConsumer, BaseS3):
    """
    JSON/JSONL 文件写入器
    将数据集写入 JSON 或 JSONL 格式的文件。
    - JSON 文件按整文件写入一行；
    - JSONL 文件按每行写入一行。

    支持路径过滤、分区、并发控制等配置。
    """

    def __init__(self, **kwargs):
        """
        初始化方法

        paths: 路径列表#list[str]#单个或多个文件/目录路径，可混合 JSON 与 JSONL 文件
        lines: 行分隔模式#bool#是否启用 JSONL 模式（按行读取/写入）
        filesystem: 文件系统#pyarrow.fs.FileSystem#用于读写文件的文件系统对象（默认根据路径自动推断）
        ray_remote_args: Ray远程参数#dict#传递给 ray.remote() 的参数
        arrow_open_stream_args: 输入流参数#dict#传递给 pyarrow.fs.FileSystem.open_input_file 的参数
        meta_provider: 元信息提供器#Any#用于提供自定义文件元信息（已废弃）
        partition_filter: 分区过滤器#Callable#路径分区过滤函数，默认仅处理 .json/.jsonl 文件
        partitioning: 分区对象#Partitioning#描述路径组织结构（默认支持 Hive 风格分区）
        include_paths: 包含路径列#bool#是否在输出中包含文件路径字段 'path'
        ignore_missing_paths: 忽略缺失路径#bool#为 True 时忽略不存在的路径
        shuffle: 文件随机打乱#None或FileShuffleConfig#可通过配置随机种子打乱文件顺序
        arrow_json_args: JSON读取参数#dict#传递给 pyarrow.json.read_json 的选项
        file_extensions: 文件扩展名#list[str]#用于筛选文件的扩展名列表
        concurrency: 并发任务数#[1, 正无穷]#最大并发 Ray 任务数（默认自动决定）
        override_num_blocks: 块数覆盖#[1, 正无穷]#覆盖读取后数据集的 block 数（一般无需设置）
        """
        super().__init__(**kwargs)

    def run(self, dataset):
        ext_name = self.params.pop("ext_name", None)
        if ext_name:
            ext = NameProvider(ext_name)
            self.params["filename_provider"] = ext

        # 创建 CSV 写入选项，指定编码
        # from pyarrow import csv
        # write_options = csv.WriteOptions(
        #     charset="utf-8",  # 这里设置编码
        #     include_header=True  # 可选：是否包含表头
        # )
        result = dataset.write_csv(filesystem=self.fs, **self.params)
        return result


class RayWriterParquet(BaseConsumer, BaseS3):
    """
    Parquet 文件写入器
    将数据集写入 Parquet 格式文件。每个 block 对应一个输出文件。

    支持目录创建、列分区、自定义文件名、并发控制等功能。
    """

    def __init__(self, **kwargs):
        """
        初始化方法

        path: 输出路径#str#目标目录路径，所有 parquet 文件将写入该目录下
        partition_cols: 分区列#list[str]#用于按列分区输出文件（Hive 风格）
        filesystem: 文件系统#pyarrow.fs.FileSystem#用于写入文件的文件系统对象（默认根据路径推断）
        try_create_dir: 自动创建目录#bool#是否在写入前自动创建目录（默认 True）
        arrow_open_stream_args: 输出流参数#dict#用于 pyarrow.fs.FileSystem.open_output_stream 的写入配置
        filename_provider: 文件名提供器#FilenameProvider#用于自定义输出文件名
        arrow_parquet_args_fn: Parquet写入参数函数#Callable#返回每个 block 写入参数的函数，支持懒加载和不可 pickled 对象
        min_rows_per_file: 每文件最小行数#[1, 正无穷]#每个文件期望写入的最小行数（为 hint，非强制限制）
        ray_remote_args: Ray远程参数#dict#传递给 ray.remote() 的参数
        concurrency: 并发任务数#[1, 正无穷]#最大并发 Ray 写入任务数（默认自动推断）
        num_rows_per_file: 每文件行数（已废弃）#int#建议使用 min_rows_per_file 代替
        arrow_parquet_args: Parquet写入参数#dict#传递给 pyarrow.parquet.ParquetWriter 的参数集合
        mode: 写入模式#str#处理已存在文件的方式，可选：overwrite、error、ignore、append（默认 append）
        """
        super().__init__(**kwargs)

    def run(self, dataset):
        ext_name = self.params.pop("ext_name", None)
        if ext_name:
            ext = NameProvider(ext_name)
            self.params["filename_provider"] = ext
        result = dataset.write_parquet(filesystem=self.fs, **self.params)
        return result
