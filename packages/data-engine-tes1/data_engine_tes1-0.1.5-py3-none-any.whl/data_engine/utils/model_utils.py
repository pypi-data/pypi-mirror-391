import os
from functools import lru_cache
from typing import Optional, Dict
from urllib.parse import urlparse
from loguru import logger


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_model_cache_dir() -> str:
    model_cache_dir = os.environ.get("DE_MODEL_CACHE")
    if not model_cache_dir:
        de_cache_dir = os.environ.get("DE_CACHE", "~/.cache/de_cache")
        de_cache_dir = os.path.expanduser(de_cache_dir)
        model_cache_dir = os.path.join(de_cache_dir, "models")
    if not os.path.exists(model_cache_dir):
        os.makedirs(model_cache_dir, exist_ok=True)
    return model_cache_dir


def get_default_s3_conf() -> Dict[str, str]:
    """
    Build default S3 configuration from environment variables.
    """
    return {
        "aws_access_key_id": os.environ.get("MODEL_S3_AK"),
        "aws_secret_access_key": os.environ.get("MODEL_S3_SK"),
        "endpoint_url": os.environ.get("MODEL_S3_URL"),
        "style": os.environ.get("MODEL_S3_STYLE"),
        "verify": False,
    }


def ensure_cached(dir_path: str, s3_path: str, s3_conf: Dict[str, str]) -> None:
    """
    Ensure a remote S3 path is downloaded into a local directory cache.
    """
    from data_engine.utils.s3_utils import download_from_s3

    result = download_from_s3(s3_path, dir_path, s3_conf)
    return result


def get_model_path(path_or_id: str, s3_conf: Optional[Dict[str, str]] = None) -> str:
    """
    Resolve a model path which can be:
      - A local absolute path
      - An S3/KS3 URL
      - A model_id (to be fetched from MODEL_S3_ROOT)
    Downloads S3 content into a local cache directory.
    Returns the local filesystem path.
    """
    path_or_id = path_or_id.strip()
    # 1. Local absolute path
    if os.path.isabs(path_or_id):
        if not os.path.isdir(path_or_id):
            raise RuntimeError(f"模型地址不存在: {path_or_id}")
        return path_or_id.rstrip("/")

    cache_root = get_model_cache_dir()
    local_dir = os.path.join(cache_root, path_or_id)
    if os.path.exists(local_dir):
        return local_dir.rstrip("/")

    s3_conf = s3_conf or get_default_s3_conf()

    if path_or_id.startswith(("s3://", "ks3://")):
        parsed = urlparse(path_or_id)
        s3_path = parsed.netloc + parsed.path
        # local_dir = os.path.join(cache_root, s3_path)
        return ensure_cached(cache_root, s3_path, s3_conf)

    base_url = os.environ.get("MODEL_S3_ROOT", "").rstrip("/") + "/"
    s3_path = base_url + path_or_id
    return ensure_cached(cache_root, s3_path, s3_conf)


def get_asset_path(path):
    if os.path.exists(path):
        return path
    defalut_dir = os.environ.get("ENGINE_ASSETS", None) or os.path.join(
        root_dir, "assets"
    )
    tmp_path = os.path.join(defalut_dir, path)
    if os.path.exists(tmp_path):
        return tmp_path
    return path


@lru_cache()
def get_spacy_model(name):
    import spacy

    return spacy.load(name)


def get_huggingface_model(
    model_path,
    model_cls: str = None,
    load_model: bool = True,
    load_processor: bool = True,
    load_tokenizer: bool = False,
    load_config: bool = False,
    trust_remote_code: bool = True,
    use_local_only: bool = True,
    processor_cls: str = "AutoProcessor",
    tokenizer_cls: str = "AutoTokenizer",
    config_cls: str = "AutoConfig",
    **kwargs,
):
    """
    通用 HuggingFace 模型加载函数，支持按需加载模型 / 处理器 / 分词器。

    参数说明：
    - model_path: 模型名称或路径
    - model_cls: 模型类名，如 "AutoModelForCausalLM"，为 None 时自动推断
    - load_model: 是否加载模型
    - load_processor: 是否加载处理器（如 AutoProcessor）
    - load_tokenizer: 是否加载分词器（如 AutoTokenizer）
    - trust_remote_code: 是否信任远程代码
    - use_local_only: 是否仅使用本地文件，避免下载
    - processor_cls, tokenizer_cls, config_cls: 可选类名
    - kwargs: 传入模型加载的其他参数

    返回：
    - 返回值为 dict，包括按需加载的组件，如 {'model': ..., 'tokenizer': ..., 'processor': ...}
    """
    import transformers
    import torch

    result = {}
    # 加载 config（只在加载模型时需要）
    config = None
    if load_model:
        ConfigClass = getattr(transformers, config_cls)
        config = ConfigClass.from_pretrained(
            model_path,
            trust_remote_code=trust_remote_code,
            local_files_only=use_local_only,
        )

    # 加载模型
    if load_model:
        # 自动推断模型类
        if model_cls is None:
            if hasattr(config, "auto_map") and config.auto_map:
                model_cls = next(
                    (cls for cls in config.auto_map if cls.startswith("AutoModel")),
                    "AutoModel",
                )
            elif hasattr(config, "architectures") and config.architectures:
                model_cls = config.architectures[0]
            else:
                model_cls = "AutoModel"

        try:
            ModelClass = getattr(transformers, model_cls)
        except AttributeError:
            raise ValueError(f"无法在 transformers 中找到模型类：{model_cls}")

        model = ModelClass.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=trust_remote_code,
            local_files_only=use_local_only,
            **kwargs,
        )
        if torch.cuda.is_available():
            model = model.to("cuda")
        result["model"] = model

    # 加载 processor
    if load_processor:
        ProcessorClass = getattr(transformers, processor_cls)
        processor = ProcessorClass.from_pretrained(
            model_path,
            trust_remote_code=trust_remote_code,
            local_files_only=use_local_only,
        )
        result["processor"] = processor

    # 加载 tokenizer
    if load_tokenizer:
        TokenizerClass = getattr(transformers, tokenizer_cls)
        tokenizer = TokenizerClass.from_pretrained(
            model_path,
            trust_remote_code=trust_remote_code,
            local_files_only=use_local_only,
        )
        result["tokenizer"] = tokenizer
    if load_config:
        result["config"] = config
    return result
