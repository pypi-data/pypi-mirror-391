import os, sys
import pandas as pd

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

import pytest
from data_engine.processors.tool.python_module import PythonCode


def test_python_code_basic_usage():
    mapper = PythonCode(import_path="tests.test_case.MyProcessor", params={"factor": 3})
    result = mapper.process(5)
    assert result == 15


def test_missing_method():
    mapper = PythonCode(
        import_path="tests.test_case.MyProcessor", func_name="nonexistent"
    )
    with pytest.raises(AttributeError):
        mapper.process(10)


def test_invalid_import_path():
    with pytest.raises(ImportError):
        PythonCode(import_path="invalid_module.NoClass")


def test_no_params():
    mapper = PythonCode(import_path="tests.test_case.MyProcessor")
    assert mapper.process(4) == 8
