#!/usr/bin/env python3
"""
视频处理器的单元测试
"""
import os, sys
import pandas as pd

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from data_engine.processors.tool.python_code import PythonCode
from data_engine.processors.nlp.nlp_mapper_clean_html import CleanHtmlMapper


from data_engine.utils.transform import sort_and_compare, print_info
from data_engine.utils.test import test_case_list

root_dir = os.path.dirname(os.path.dirname(__file__))
case_list = [
    {
        "class": PythonCode,
        "params": {
            "code": """import pandas as pd
def aa(data) -> list:
    return [data]
"""
        },
        "input": [{"text": "我爱北京天安门"}],
        "output": [{"text": "我爱北京天安门"}],
        "compare": print_info,
    },
    {
        "class": PythonCode,
        "params": {
            "code": """import pandas as pd
def aa(data):
    return data
"""
        },
        "input": [{"text": "我爱北京天安门"}],
        "output": [{"text": "我爱北京天安门"}],
        "compare": print_info,
    },
    {
        "class": PythonCode,
        "params": {
            "code": """import pandas as pd

def aa(data: pd.DataFrame):
    print(f"======********=={type(data)}")
    return data
"""
        },
        "input": [{"text": "我爱北京天安门"}],
        "output": [{"text": "我爱北京天安门"}],
        "compare": print_info,
    },
]


if __name__ == "__main__":
    test_case_list(case_list)
