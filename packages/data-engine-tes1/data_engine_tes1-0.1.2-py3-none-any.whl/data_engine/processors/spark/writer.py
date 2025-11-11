import ray, copy, json, time
from data_engine.core.base import BaseConsumer
from data_engine.utils.log_utils import default_serializer


# 反序列化查看原始数据
def deserialize(d):
    if isinstance(d, dict):
        return {k: default_serializer(v) for k, v in d.items()}
    return d


class SparkWriterJsonline(BaseConsumer):
    def run(self, data):
        from data_engine.core.factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("spark")

        df = executor.spark.createDataFrame(data)
        result = df.write.json(**self.params)
        return result


class SparkWriter(BaseConsumer):
    """
    Spark DataFrame Writer
    支持将 DataFrame 保存到指定路径，支持 json, csv, parquet 等。
    使用示例：
        params = {"path": "data/output.json", "format": "json", "mode": "overwrite", "options": {"compression": "gzip"}}
        writer = SparkWriterDataFrame(params=params)
        writer.run(df)

        format：文件格式,如csv,json,parquet
        mode：写入模式:overwrite(覆盖)/ append(追加) / ignore(忽略)/errorifexists(存在则报错)
    """

    def run(self, data):
        kwargs = self.params.copy()
        print(f"SparkWriter kwargs:{kwargs}")
        path = kwargs.pop("path", "result")
        fmt = kwargs.pop("format", "parquet")  # 默认 parquet
        if fmt == "csv":
            kwargs["header"] = True
        # 禁用 _SUCCESS
        kwargs["spark.sql.sources.writeJobSuccessFile"] = False

        mode = kwargs.pop("mode", "errorifexists")  # 默认 error
        schema = kwargs.pop("schema", None)

        if data is None:
            raise ValueError("SparkWriterDataFrame: 输入 DataFrame 不能为空")

        from data_engine.core.factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("spark")
        spark = executor.spark

        from pyspark.rdd import RDD

        if isinstance(data, RDD):
            # 特殊类型的数据处理
            if data is None:
                raise ValueError("SparkWriterDataFrame: 输入 DataFrame 不能为空")
            data = data.map(deserialize)
            if schema is not None:
                df = spark.createDataFrame(data, schema=schema)
            else:
                df = spark.createDataFrame(data)
        else:
            df = data
        result = df.write.format(fmt).mode(mode).options(**kwargs).save(path)
        return result
