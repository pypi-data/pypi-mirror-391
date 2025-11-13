import copy
from data_engine.utils.transform import sort_and_compare, camel_to_snake
from data_engine.core.factory import ExecutorFactory
from data_engine.define import ExecutorType
from data_engine.core.base import Pipeline
from data_engine.processors.ray.reader import RayReaderFromItems
from data_engine.processors.ray.tool import ToolTakeAll
from data_engine.utils.error import ExecutorError


def test_case_list(case_list):
    executor_type = ExecutorType("ray")
    executor = ExecutorFactory.create_executor(executor_type)
    ds = None
    for index, case in enumerate(case_list):
        process_params = case["params"]
        process_params["_engine_config"] = case.get("_engine_config", "")  # wjw
        process_params["kwargs"] = copy.deepcopy(process_params)
        processor_list = [
            RayReaderFromItems(items=case["input"]),
            case["class"](**process_params),
            ToolTakeAll(),
        ]
        # pipeline = Pipeline(processor_list, executor)
        # result = pipeline.process()
        for op_instance in processor_list:
            # print(f'--op_instance:{op_instance}')
            ds = executor.run(ds, op_instance)
            print(f"--1---真实result ds:{ds}")
            print(f'--2---预测result:{case["output"]}')
        case_result = case["compare"](case["output"], ds)

    ds = executor.finish(ds)


from pyspark.sql import SparkSession


def test_case_list_spark(case_list):
    # 初始化 Spark
    spark = (
        SparkSession.builder.appName("SparkPipelineTest")
        .config("spark.master", "local[*]")
        .config("spark.submit.deployMode", "client")
        .getOrCreate()
    )

    sc = spark.sparkContext

    executor_type = ExecutorType("spark")
    executor = ExecutorFactory.create_executor(executor_type)

    for index, case in enumerate(case_list):
        process_params = case["params"]
        process_params["kwargs"] = copy.deepcopy(process_params)

        # Step 1: 把输入数据变成 RDD
        rdd = sc.parallelize(case["input"])

        # Step 2: 依次应用处理器
        # case["class"] 需要是可在 map 中调用的函数式处理器
        processor = case["class"](**process_params)
        try:
            rdd = executor.run(rdd, processor)
        except ExecutorError as e:
            continue
        # rdd = rdd.map(lambda x: processor.process(x))

        # ToolTakeAll 等价于 collect
        result = rdd.collect()

        # Step 3: 比较结果
        case_result = case["compare"](case["output"], result)
        print(f"========index: {index} result: {case_result}==========")

    spark.stop()
