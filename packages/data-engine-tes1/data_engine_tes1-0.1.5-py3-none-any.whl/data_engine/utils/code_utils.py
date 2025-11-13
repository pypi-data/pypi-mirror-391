import inspect
import pandas as pd


def get_single_param_type(func):
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    # 检查是否有且只有一个参数
    # if len(params) != 1:
    #     raise ValueError("函数必须有且仅有一个参数")

    param = params[0]

    # 先尝试获取类型注解
    if param.annotation is not inspect.Parameter.empty:
        return param.annotation

    # 再尝试从默认值推断类型
    if param.default is not inspect.Parameter.empty:
        return type(param.default)

    # 如果两者都没有
    return None
