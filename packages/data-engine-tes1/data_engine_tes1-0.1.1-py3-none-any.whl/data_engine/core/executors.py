import os
from typing import Any, Callable, Optional, Union, Dict
from loguru import logger
from data_engine.core.base import Executor, BaseProcessor
from data_engine.define import OpType
from typing import get_type_hints, NoReturn
import pandas as pd
from data_engine.utils.code_utils import get_single_param_type
from data_engine.utils.error import ExecutorError
from data_engine.utils.log_utils import deserialize


class HuggingFaceExecutor(Executor):
    """Executor that uses HuggingFace datasets for data processing."""

    def __init__(self):
        """Initialize the PySparkExecutor."""
        pass

    def process(self, dataset, process_obj: BaseProcessor):
        """Apply a map function to the data using Ray datasets.

        Args:
            data: The input data to map
            func: The function to apply to each element

        Returns:
            The mapped data
        """
        if process_obj.use_class:
            raise ExecutorError("PySparkExecutor does not support use_class=True")
        kwargs = process_obj.kwargs
        exec_params = kwargs.pop("exec_params", {}) or {}
        if process_obj.op_type in (
            OpType.READER,
            OpType.CONSUMER,
            OpType.TOOL,
        ):
            dataset = process_obj.process(dataset)
        else:
            dataset = dataset.map(process_obj.run)
        return dataset


class RayExecutor(Executor):
    """Executor that uses Ray datasets for distributed data processing."""

    def finish(self, ds):
        import ray

        named_actors = ray.util.list_named_actors(all_namespaces=True)

        for actor_info in named_actors:
            try:
                # 通过名称获取 actor handle
                if actor_info["name"].startswith("global"):
                    actor_handle = ray.get_actor(
                        actor_info["name"], namespace=actor_info["namespace"]
                    )
                    ray.kill(actor_handle, no_restart=True)
            except Exception as e:
                pass
        ray.serve.shutdown()
        ray.shutdown()
        return super().finish(ds)

    def start(self, config):
        import ray

        config = config or {}
        params = {}
        for config_name, ray_config in (("envs", "env_vars"), ("pip", "pip")):
            v = config.get(config_name)
            if v:
                params[ray_config] = v

        ray.init(address="auto", runtime_env=params, ignore_reinit_error=True)
        from ray.data import DataContext

        context = DataContext.get_current()
        context.enable_op_resource_reservation = False
        context.op_resource_reservation_ratio = 0.1

    def process(self, dataset, process_obj: BaseProcessor):
        """Apply a map function to the data using Ray datasets.

        Args:
            data: The input data to map
            func: The function to apply to each element

        Returns:
            The mapped data
        """
        import ray

        kwargs = process_obj.kwargs
        kwargs["_engine_config"] = process_obj._engine_config
        ray_kwargs = kwargs.pop("exec_params", {}) or {}
        hints = get_type_hints(process_obj.process)
        param_type = getattr(process_obj, "_param_type", None) or get_single_param_type(
            process_obj.process
        )
        return_type = getattr(process_obj, "_return_type", None) or hints.get(
            "return", None
        )
        if return_type is NoReturn or return_type == "NoReturn":
            return process_obj.run(dataset)

        if return_type is list:
            exec_function = getattr(
                dataset,
                "flat_map",
            )
        elif param_type is pd.DataFrame:
            exec_function = getattr(
                dataset,
                "map_batches",
            )
            ray_kwargs["batch_format"] = "pandas"
        else:
            exec_function = getattr(
                dataset,
                "flat_map",
            )
        if process_obj.use_class:
            kwargs["kwargs"] = {"use_class": True}
            if "concurrency" not in ray_kwargs:
                ray_kwargs["concurrency"] = (1, 100000)
            if isinstance(ray_kwargs["concurrency"], list):
                ray_kwargs["concurrency"] = tuple(ray_kwargs["concurrency"])
            op_class = type(process_obj)

            dataset = exec_function(
                op_class,
                fn_constructor_kwargs=kwargs,
                **ray_kwargs,
            )
        else:
            dataset = exec_function(
                process_obj.run,
                **ray_kwargs,
            )
        return dataset


class SparkExecutor(Executor):
    """Executor that uses Ray datasets for distributed data processing."""

    def process(self, dataset, process_obj: BaseProcessor):
        """Apply a map function to the data using Ray datasets.

        Args:
            data: The input data to map
            func: The function to apply to each element

        Returns:
            The mapped data
        """
        only_ray = getattr(process_obj, "only_ray", None)
        if process_obj.use_class or only_ray:
            raise ExecutorError("本算法仅支持RAY 分布式引擎")
        kwargs = process_obj.kwargs
        kwargs["_engine_config"] = process_obj._engine_config
        hints = get_type_hints(process_obj.process)
        return_type = getattr(process_obj, "_return_type", None) or hints.get(
            "return", None
        )
        if return_type is NoReturn or return_type == "NoReturn":
            # spark tool使用，将rdd转dataframe
            from pyspark.rdd import RDD

            if isinstance(dataset, RDD):
                # RDD为空，直接返回。(未获取到数据，请检查数据集和工作流算子参数配置)
                if dataset.isEmpty():
                    logger.warning(
                        f"No data retrieved.please check the dataset and the parameter configuration of workflow operators.parameters:{kwargs.get('path','')}"
                    )
                    return

                dataset = dataset.map(deserialize)
                dataset = self.spark.createDataFrame(dataset)
            return process_obj.run(dataset)
        else:
            from pyspark.sql import DataFrame

            if isinstance(dataset, DataFrame):
                # dataset = dataset.rdd
                dataset = dataset.rdd.map(lambda row: row.asDict())
            dataset = dataset.flatMap(
                process_obj.run,
            )
        return dataset

    def finish(self, ds):
        self.spark.stop()
        return super().finish(ds)

    def start(self, config):
        # 从参数里读取运行模式，默认 local
        config = config or {}
        from pyspark.sql import SparkSession
        from pyspark import SparkConf

        master = config.pop("master", "yarn")
        app_name = config.pop("app_name", "JSONL_Reader")

        # 创建SparkConf对象，加载字典配置
        conf = SparkConf()
        for env_name in [
            "spark_driver_memory",
            "spark_driver_cores",
            "spark_executor_memory",
            "spark_executor_cores",
        ]:
            env_value = config.get(env_name, "")
            # print(f"spark conf setting1111:{env_name} = {env_value}")
            if env_value and str(env_value).strip() != "0":
                if "memory" in env_name:
                    env_value = f"{env_value}g"
                # print(f"spark conf setting:{env_name} = {env_value}")
                logger.info(f"spark conf setting:{env_name} = {env_value}")
                # SparkConf.set() 支持链式调用
                conf = conf.set(env_name.replace("_", "."), env_value)
                # print(f"spark start conf yaml setting:{env_name} = {env_value}")

        logger.info(f"spark run conf finally all set :{conf.getAll()}")

        spark = (
            SparkSession.builder.appName(app_name)
            .config(conf=conf)
            .master(master)  # local[*] / yarn
            .getOrCreate()
        )
        self.spark = spark
