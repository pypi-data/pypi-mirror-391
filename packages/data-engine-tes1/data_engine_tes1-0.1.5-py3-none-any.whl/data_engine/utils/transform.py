import re, os
import ast
from typing import Any, Dict, Union, Optional, Tuple
from loguru import logger
from data_engine.define import ExecutorType


_UNIT_MAP = {
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
}


def replace_var(match, variables):
    var_name = match.group(1)
    return variables.get(var_name, match.group(0))


def _parse_memory_str(s: str) -> int:
    s = s.strip().upper()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([KMG]B)$", s)
    if not m:
        raise ValueError(f"无法解析内存字符串: {s!r}")
    number, unit = m.groups()
    return int(float(number) * _UNIT_MAP[unit])


def transform_structure(obj, replace_data):
    if not replace_data:
        return obj
    if isinstance(obj, dict):
        new_d = {}
        for k, v in obj.items():
            if k == "memory" and isinstance(v, str):
                new_d[k] = _parse_memory_str(v)
            else:
                new_d[k] = transform_structure(v, replace_data)
        return new_d

    elif isinstance(obj, list):
        return [transform_structure(x, replace_data) for x in obj]
    elif isinstance(obj, tuple):
        return tuple(transform_structure(x, replace_data) for x in obj)

    elif isinstance(obj, str):
        name_all = re.match(r"^\$\{(\w+)\}$", obj)
        if name_all:
            return replace_data[name_all.group(1)]
        result = re.sub(r"\$\{(\w+)\}", lambda x: replace_var(x, replace_data), obj)
        return result

    else:
        return obj


def sort_and_compare(expect, output):
    if isinstance(expect, dict) and isinstance(output, dict):
        if set(expect.keys()) != set(output.keys()):
            return False
        return all(sort_and_compare(expect[k], output[k]) for k in expect)

    elif isinstance(expect, list) and isinstance(output, list):
        if len(expect) != len(output):
            return False
        # 递归地对每个元素进行规范化（排序/排序后的比较）
        sorted1 = sorted([normalize(e) for e in expect], key=sort_key)
        sorted2 = sorted([normalize(e) for e in output], key=sort_key)
        return all(sort_and_compare(a, b) for a, b in zip(sorted1, sorted2))

    else:
        return expect == output


def print_info(expect, output):
    logger.info("output:{}  expect:{}", expect, output)
    return {"expect": expect}


def auto_update_placeholder_output(expect, output):
    """
    自动捕获输出结果并更新测试文件中的#output#占位符
    """
    import sys
    import inspect
    import json

    # 检查是否启用了自动更新功能
    if "--uo" not in sys.argv:
        # 如果没有启用自动更新，则直接返回True，正常执行测试
        return True

    logger.info("捕获到实际输出: {}", output)

    try:
        # 获取调用栈，找到测试文件路径
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        # 继续向上查找，直到找到测试文件（不是test.py）
        while caller_frame and (
            "test.py" in caller_frame.f_code.co_filename
            and "data_engine/utils" in caller_frame.f_code.co_filename
        ):
            caller_frame = caller_frame.f_back

        if not caller_frame:
            logger.warning("无法找到调用测试文件")
            return True

        test_file_path = caller_frame.f_code.co_filename

        # 确保获取到的是正确的测试文件路径
        logger.info("调用文件路径: {}", test_file_path)

        # 读取测试文件内容
        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 将输出结果转换为Python格式的字符串（不带引号）
        # 使用 pprint 来获取更好的格式化
        import pprint

        output_str = pprint.pformat(output, width=1000)

        # updated_content = content.replace('#output#', output_str)
        if '"#output#"' in content:
            updated_content = content.replace('"#output#"', output_str)

        logger.info("--output_str--: {}", output_str)
        # logger.info("1要更新的文件内容--: {}", updated_content)

        # 把auto_update_placeholder_output替换为sort_and_compare
        updated_content = updated_content.replace(
            "auto_update_placeholder_output", "sort_and_compare"
        )
        logger.info("2要更新的文件内容--: {}", updated_content)

        # 写入更新后的内容
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        #     logger.info("已自动更新测试文件: {}", test_file_path)
        #     logger.info("新的output值: {}", output_str)
        # else:
        #     logger.warning("未找到#output#占位符")
    except Exception as e:
        logger.warning("自动更新测试文件失败: {}", e)
        import traceback

        logger.warning("详细错误信息: {}", traceback.format_exc())

    # 返回True使测试继续执行
    return True


def normalize(obj):
    """用于排序时对复杂结构进行统一转换"""
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return sorted([normalize(e) for e in obj], key=sort_key)
    return obj


def sort_key(obj):
    """为排序复杂结构生成 key"""
    return str(obj)


def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase to snake_case.
    """
    # Insert underscore between lower-to-upper or digit-to-letter transitions
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return snake


def extract_class_paths(
    register_file: str, executor_type: Optional[ExecutorType] = None
) -> Dict[str, Tuple[str, str]]:
    """
    扫描 register_file 中所有 data_engine.processors 下的 from ... import ... 语句。

    - 如果模块路径不是以 data_engine.processors.{SPARK|HF|RAY} 开头，
      则无条件保留。
    - 如果模块路径属于上述三种 executor 中的一种，
      则仅当它与传入的 executor_type 相匹配时才保留；否则跳过。
    """
    mapping: Dict[str, Tuple[str, str]] = {}
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    register_file = os.path.join(root_dir, register_file)
    src = open(register_file, encoding="utf-8").read()
    tree = ast.parse(src, filename=register_file)

    # 三种 executor 的前缀
    prefixes = {
        ExecutorType.SPARK: "data_engine.processors." + ExecutorType.SPARK.value,
        ExecutorType.HF: "data_engine.processors." + ExecutorType.HF.value,
        ExecutorType.RAY: "data_engine.processors." + ExecutorType.RAY.value,
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module_path = node.module or ""
        if not module_path.startswith("data_engine.processors."):
            continue

        # 检查它是否属于 Spark/HF/Ray 中的某一种
        matched = None
        for etype, prefix in prefixes.items():
            if module_path.startswith(prefix):
                matched = etype
                break

        # 如果属于三种之一，则根据 executor_type 决定是否跳过
        if (
            matched is not None
            and executor_type is not None
            and matched != executor_type
        ):
            continue
        # 否则（不属于三种之一 或 与 executor_type 匹配），一律保留

        # 收集导入的类
        for alias in node.names:
            cls_name = alias.name
            key = camel_to_snake(cls_name)
            mapping[key] = (module_path, cls_name)

    return mapping
