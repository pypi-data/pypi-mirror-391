import json, sys, re, os, copy, shutil
from pathlib import Path
from loguru import logger
from typing import Dict
from collections import defaultdict
import importlib
import zipfile

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)
from data_engine.define import ExecutorType
from data_engine.core.base import Pipeline
from data_engine.core.factory import ExecutorFactory
from data_engine.utils.transform import transform_structure, extract_class_paths
from data_engine.utils.s3_utils import download_from_s3

try:
    importlib.import_module("data_engine.processors.video_split_by_scene")
except ImportError:
    pass


# 尝试导入可选依赖
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml

    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


def from_file(file_path: str) -> "Pipeline":
    """从文件创建Pipeline实例。

    支持的文件格式：
    - YAML (.yml, .yaml)
    - TOML (.toml)
    - JSON (.json)

    Args:
        file_path: 配置文件路径

    Returns:
        Pipeline实例

    Raises:
        ValueError: 不支持的文件格式或缺少必要的依赖包
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix in (".yml", ".yaml"):
        if not YAML_AVAILABLE:
            raise ImportError("导入YAML需要安装PyYAML库: pip install pyyaml")
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
    elif suffix == ".toml":
        if not TOML_AVAILABLE:
            raise ImportError("导入TOML需要安装toml库: pip install toml")
        with open(file_path, "r") as f:
            config = toml.load(f)
    elif suffix == ".json":
        with open(file_path, "r") as f:
            config = json.load(f)
    else:
        raise ValueError(f"不支持的文件格式: {suffix}")
    workspace = config["workspace"] = config.get("workspace") or os.getcwd()
    vars = {"workspace": workspace}
    vars.update(os.environ)
    config_vars = config.get("vars", {})
    config_vars = transform_structure(config_vars, os.environ)
    vars.update(config_vars)
    config = transform_structure(config, vars)
    logger.info(f"config: {config}")

    envs = config.get("envs") or {}
    if "UDF_PATH" not in envs:
        envs["UDF_PATH"] = "/opt/self_code"
    envs["workspace"] = workspace
    envs["working_dir"] = workspace
    os.chdir(workspace)

    if envs:
        os.environ.update(envs)
    config["envs"] = envs
    return config


def download_udf(workspace, s3_conf, process_params):
    if not s3_conf:
        from data_engine.utils.path_utils import get_udf

        udf_path = get_udf(workspace)
        download_dir = os.path.join(udf_path, "s3-udf-download")
        if os.path.exists(udf_path):
            shutil.rmtree(udf_path)
        os.makedirs(download_dir, exist_ok=True)
        s3_conf = process_params.get("s3_conf") or {}
        if not s3_conf:
            s3_conf = {
                "aws_access_key_id": os.environ["S3AK"],
                "aws_secret_access_key": os.environ["S3SK"],
                "endpoint_url": os.environ["S3URL"],
                "verify": False,
            }
    s3_path = process_params["s3_path"]
    result = download_from_s3(s3_path, download_dir, s3_conf)
    with zipfile.ZipFile(result) as zf:
        zf.extractall(udf_path)
    return s3_conf


def main():
    conifg_path = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
    config = from_file(conifg_path)
    if config.get("display_config"):
        logger.info(f"display config: {yaml.dumps(config)}")
    executor_type = ExecutorType.from_str(config.get("executor"))

    # 获取处理器类路径映射
    # file_path = os.path.join(root_dir, "data_engine/processors/register.py")
    op_dict = extract_class_paths("processors/register.py", executor_type)
    executor = ExecutorFactory.create_executor(executor_type, config)

    processor_list = []
    engine_config = {}
    for k, v in config.items():
        if k in ("processors", "envs", "vars"):
            continue
        engine_config[k] = v
    if config.get("display_all_processors"):
        names = list(op_dict.values())
        logger.info(f"display all processors: {names}")

    s3_conf = {}
    process_index = defaultdict(int)
    ds_dict = {}
    ds = None
    server_list = config.get("servers", [])
    if server_list:
        from ray import serve
        from ray.serve.llm import LLMConfig, build_openai_app

    server_config = []
    for server_dict in server_list:
        server_config.append(LLMConfig(**server_dict))
        app = build_openai_app({"llm_configs": server_config})
        serve.run(app, blocking=False)
    for process_dict in config["processors"]:
        process_name, process_params = list(process_dict.items())[0]
        process_params = process_params or {}
        for k, v in process_params.items():
            if isinstance(v, str) and v in ds_dict:
                process_params[k] = ds_dict[v]

        moudle_path, cls_name = op_dict[process_name]
        logger.info(f"moudle_path: {moudle_path}, cls_name: {cls_name}")
        moudle = importlib.import_module(moudle_path)
        if process_name == "python_module":
            download_udf(config["workspace"], s3_conf, process_params)
        process_params.update(
            {
                "_engine_config": copy.deepcopy(engine_config),
                "kwargs": copy.deepcopy(process_params),
            }
        )
        process_params["_engine_config"]["_relative_index"] = process_index[
            process_name
        ]
        op_cls = getattr(moudle, cls_name)
        process_params["_engine_config"]["_class"] = op_cls
        op_instance = op_cls(**process_params)
        processor_list.append(op_instance)
        process_index[process_name] += 1
        ds = executor.run(ds, op_instance)
    if ds:
        logger.info("执行结果为：{} ", ds)


if __name__ == "__main__":
    main()
