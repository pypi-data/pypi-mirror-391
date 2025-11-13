import ast
from data_engine.core.base import BaseMapper
from data_engine.utils.code_utils import get_single_param_type
from typing import get_type_hints, NoReturn


class PythonCode(BaseMapper):
    """
    执行python代码
    输入python 代码执行
    例如：
    import pandas as pd
    def aa(data):
        return data
    """

    def __init__(
        self,
        code: str,
        func_name: str = "process",
        data_type: str = "data",
        params: dict = None,
        **kwargs
    ):
        """
        初始化方法
        code: python代码#需要执行的python代码
        data_type: 算子输入的数据类型#[data, dataset]#data表示单行数据，dataset表示整个数据集
        """
        super().__init__(**kwargs)
        self.lambda_func = self._create_lambda(code, func_name)
        self._param_type = get_single_param_type(self.lambda_func)
        self._return_type = get_type_hints(self.lambda_func).get("return", None)
        self.params = params
        self.data_type = data_type
        if self.data_type != "data":
            self._return_type = "NoReturn"

    def _create_lambda(self, func_str: str, func_name: str):
        func_str = func_str.encode("utf-8").decode("unicode_escape")
        tree = ast.parse(func_str)
        func_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        code_obj = compile(tree, filename="<string>", mode="exec")
        namespace = {}
        exec(code_obj, namespace)
        if len(func_defs) == 1:
            func_name = func_defs[0].name
        else:
            func_name = func_name

        return namespace[func_name]

    def process(self, data):
        if self.use_class:
            data = (
                self.lambda_func(self, data, **self.params)
                if self.params
                else self.lambda_func(self, data)
            )
        else:
            data = (
                self.lambda_func(data, **self.params)
                if self.params
                else self.lambda_func(data)
            )

        return data

    def run(self, dataset):
        if self.data_type == "data":
            return super().run(dataset)
        else:
            dataset = (
                self.lambda_func(dataset, **self.params)
                if self.params
                else self.lambda_func(dataset)
            )
            return dataset
