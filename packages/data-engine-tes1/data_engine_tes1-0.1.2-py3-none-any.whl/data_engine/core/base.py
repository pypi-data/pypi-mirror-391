from abc import ABC, abstractmethod
from typing import Any, Callable, List, Union, Dict, Optional, NoReturn
from loguru import logger
import copy, json, os
import pandas as pd
from data_engine.define import ExecutorType
from data_engine.define import OpType
from data_engine.utils.code_utils import get_single_param_type
from data_engine.utils.log_utils import RayDataErrorLogger
from data_engine.utils.transform import camel_to_snake


class Base:
    def __init__(self, **kwargs):
        super().__init__()


class BaseProcessor(Base):
    """Base abstract class for all data processors."""

    use_class = False

    op_type: str = OpType.MAPPER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.get("kwargs", {}) or {}
        if "use_class" in self.kwargs:
            self.use_class = self.kwargs.pop("use_class")

    def get_default_dir(self, dir, ext=""):
        base_dir = self._engine_config["workspace"]
        if dir:
            result = os.path.join(base_dir, "result", dir)
            os.makedirs(result, exist_ok=True)
            return result

        class_name = self._engine_config["_class"].__name__
        class_name = camel_to_snake(class_name)
        _relative_index = self._engine_config["_relative_index"]
        path = os.path.join(base_dir, "result", f"{class_name}_{_relative_index}")
        if ext:
            path = f"{path}_{ext}"
        os.makedirs(path, exist_ok=True)
        return path

    def process(self, data: Any) -> NoReturn:
        """Process the data using the provided executor.

        Args:
            data: The input data to process
            executor: The executor to use for processing

        Returns:
            The processed data
        """
        pass

    def run(self, data):
        executor_type = ExecutorType.from_str(self._engine_config.get("executor"))
        data_error_directory = self._engine_config.get("data_error_directory")
        raise_error = self._engine_config.get("raise_error") or False

        try:
            data = self.process(data)
            if isinstance(data, list):
                if not data:
                    data = []
            elif isinstance(data, dict):
                if not data:
                    data = []
                else:
                    data = [data]
            return data
        except Exception as e:
            logger.exception("process name: {} error msg {}", type(self).__name__, e)
            if data_error_directory:
                data_logger = RayDataErrorLogger(data_error_directory)
                data_logger.log_error(data, str(e), str(self.__class__.__name__))

            if raise_error:

                raise e
            data_type = get_single_param_type(self.process)
            if data_type is pd.DataFrame:
                data = pd.DataFrame([])
            else:
                data = []
        return data

    def __call__(self, data):
        return self.run(data)


class BaseFilter(BaseProcessor):
    op_type: str = OpType.FILTER

    def __init__(self, do_filter=False, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.get("kwargs", {}) or {}
        self.do_filter = do_filter


class BaseS3(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        s3_conf = kwargs.get("s3_conf")
        self.fs = None
        if s3_conf:
            conf = {
                "aws_access_key_id": s3_conf["ak"],
                "aws_secret_access_key": s3_conf["sk"],
                "endpoint_url": s3_conf["url"],
                "verify": False,
            }
            s3_url_style = s3_conf.get("style", None) or os.environ.get(
                "S3_URL_STYLE", "auto"
            )
            import s3fs

            self.fs = s3fs.S3FileSystem(
                anon=False,
                use_ssl=False,
                client_kwargs=conf,
                config_kwargs={
                    "s3": {"addressing_style": s3_url_style},
                    "connect_timeout": 10,
                    "read_timeout": 300,
                },
            )


class BaseMapper(BaseProcessor):
    op_type: str = OpType.MAPPER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.get("kwargs", {}) or {}


class BaseTool(BaseProcessor):
    op_type: str = OpType.TOOL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.get("kwargs", {}) or {}


class BaseReader(BaseProcessor):
    op_type: str = OpType.READER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.pop("kwargs", {}) or {}
        self.params = {}

        for k, v in kwargs.items():
            if not k.startswith("_engine") and k != "s3_conf":
                self.params[k] = copy.deepcopy(v)


class BaseConsumer(BaseProcessor):
    op_type: str = OpType.CONSUMER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._engine_config = kwargs.get("_engine_config", {}) or {}
        self.kwargs = kwargs.pop("kwargs", {}) or {}
        self.params = {}  # 去除框架参数

        skip_keys = ("s3_conf",)
        workspace = self._engine_config.get("workspace")

        for k, v in self.kwargs.items():
            if k.startswith("_engine") or k in skip_keys:
                continue
            if k == "path":
                v = v or ""
                v = v.strip()
                if "s3_conf" not in self.kwargs and not v.startswith("/"):
                    v = os.path.join(workspace, "result", v)

            self.params[k] = copy.deepcopy(v)


class Pipeline:
    """A pipeline of processors that can be executed together."""

    def __init__(self, processor_list, executor):
        self.executor = executor
        self.processor_list = processor_list

    def process(
        self,
        data: Any = None,
    ) -> Any:
        """Process the data through all processors in the pipeline.

        Args:
            data: The input data to process
            executor: The executor to use for processing

        Returns:
            The processed data after going through all processors
        """
        for processor in self.processor_list:
            data = self.executor.run(data, processor)
        data = self.executor.finish(data)
        return data


class Executor(ABC):
    """Base abstract class for all executors."""

    def __init__(self, config):
        self.start(config)

    def process(self, data: Any, process_obj) -> Any:
        """Apply a map function to the data.

        Args:
            data: The input data to map
            func: The function to apply to each element

        Returns:
            The mapped data
        """
        pass

    def start(self, config):
        return None

    def finish(self, ds):
        return ds

    def run(self, data: Any, process_obj):
        try:
            return self.process(data, process_obj)
        except Exception as e:
            logger.exception(f"process name: {type(process_obj).__name__} ")
            raise e
