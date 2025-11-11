import json, re
from pyspark.sql import SparkSession
from data_engine.core.base import BaseReader


class SparkReaderJsonline(BaseReader):

    def run(self, data):
        kwargs = self.params
        path = kwargs.pop("path")
        from data_engine.core.factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("spark")
        rdd = executor.spark.sparkContext.textFile(path, **kwargs)
        rdd = rdd.map(lambda line: json.loads(line))

        return rdd


class SparkReader(BaseReader):
    """
    Spark DataFrame Reader
    支持读取多种格式的 DataFrame，例如 json, csv, parquet 等。
    使用示例：
        params = {"path": "data/input.json", "format": "json", "multiline": "true"}
        "path": "字符串或列表，指定JSON文件路径/目录/通配符模式"
        "format":csv"：逗号分隔值文件
                "json"：JSON 格式文件（支持单行 JSON 或多行 JSON）
                "parquet"：Parquet 列式存储文件（Spark 默认格式，高效压缩）
        "multiLine": "布尔值,一条json数据是否跨多行,默认False,针对json格式有效"

        reader = SparkReader(params=params)
        df = reader.run(None)
    """

    def run(self, data):
        kwargs = self.params.copy()
        paths = kwargs.pop("paths")
        paths = re.split(r"\s*,\s*", paths.strip())
        fmt = kwargs.pop("format", "parquet")  # 默认 parquet
        if fmt == "csv":
            kwargs["header"] = True
        from data_engine.core.factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("spark")

        df = executor.spark.read.format(fmt).options(**kwargs).load(paths)
        # import time
        # time.sleep(500)
        return df
