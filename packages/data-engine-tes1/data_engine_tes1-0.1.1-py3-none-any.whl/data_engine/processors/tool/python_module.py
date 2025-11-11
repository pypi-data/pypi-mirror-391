import importlib, os
import sys
from data_engine.core.base import BaseMapper
from data_engine.utils.path_utils import get_udf

udf_path = get_udf()
if udf_path not in sys.path:
    sys.path.append(udf_path)


class PythonModule(BaseMapper):
    def __init__(
        self,
        s3_path: str,
        import_path: str = None,
        name=None,
        params=None,
        func_name="process",
        s3_conf: dict = None,
        data_type="data",
        **kwargs,
    ):
        """
        初始化方法
        s3_path: s3地址#s3地址
        name: 自定义算子名称#自定义算子名称
        params: 参数#参数
        """
        super().__init__(**kwargs)
        self.data_type = data_type
        print(list(os.walk(udf_path)))
        if not import_path:
            import_path = f"{name}.main.MyProcessor"
        try:
            module_path, class_name = import_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            target_class = getattr(module, class_name)
        except (ValueError, ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import {import_path}: {e}")

        self.instance = target_class(**params) if params else target_class()
        self.params = params
        self.func_name = func_name
        if not hasattr(self.instance, self.func_name):
            raise AttributeError(f"{self.instance} has no method '{self.func_name}'")

    def process(self, data):
        return getattr(self.instance, self.func_name)(data)

    def run(self, dataset):
        if self.data_type == "data":
            return super().run(dataset)
        else:
            return getattr(self.instance, self.func_name)(dataset)
