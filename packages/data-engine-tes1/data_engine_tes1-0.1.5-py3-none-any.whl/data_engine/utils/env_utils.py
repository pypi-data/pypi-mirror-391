# tool/utils/env_utils.py
import os
import sys
import json
import logging
import shutil
import shlex
import subprocess
from typing import Tuple, Optional
from data_engine.utils.s3_utils import download_from_s3  # existing project helper

logger = logging.getLogger(__name__)


def exit_with_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_s3_conf() -> dict:
    ak = os.environ.get("S3AK")
    sk = os.environ.get("S3SK")
    url = os.environ.get("S3URL")
    if not (ak and sk and url):
        return {}
    verify_env = os.environ.get("S3VERIFY", "false").strip().lower()
    return {
        "aws_access_key_id": ak,
        "aws_secret_access_key": sk,
        "endpoint_url": url,
        "verify": verify_env in {"1", "true", "yes"},
    }


def read_config_executor(config_path: str, run_path: str) -> Tuple[str, str]:
    """
    Return (executor, local_config_path).
    If config_path is s3://... then download to run_path/config/.
    Supports .yaml/.yml/.json. Defaults to 'ray' if missing.
    """
    s3_conf = ensure_s3_conf()
    if config_path.startswith("s3://"):
        if not s3_conf:
            exit_with_error(
                "S3 credentials are required for s3 config path (S3AK/S3SK/S3URL)"
            )
        try:
            local_dir = os.path.join(run_path, "config")
            os.makedirs(local_dir, exist_ok=True)
            config_path = download_from_s3(config_path, local_dir, s3_conf)
        except Exception as e:
            exit_with_error(f"Failed to download config from S3: {e}")

    suffix = os.path.splitext(config_path)[1].lower()
    executor = None
    try:
        if suffix in (".yml", ".yaml"):
            try:
                import yaml  # type: ignore
            except Exception:
                exit_with_error("yaml config provided but PyYAML not installed")
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            executor = (cfg.get("executor") or "ray").lower()
        elif suffix == ".json":
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            executor = (cfg.get("executor") or "ray").lower()
        else:
            logger.warning("Unknown config extension; defaulting executor to 'ray'")
            executor = "ray"
    except FileNotFoundError:
        exit_with_error(f"Config not found: {config_path}")
    except Exception as e:
        exit_with_error(f"Failed to parse config: {e}")

    if not executor:
        executor = "ray"
    return executor.lower(), config_path


def run_with_logging(cmd, cwd: Optional[str] = None, env: Optional[dict] = None):
    """Run command, stream combined stdout/stderr to STDOUT, exit 1 on failure."""
    if isinstance(cmd, (list, tuple)):
        display = " ".join(shlex.quote(c) for c in cmd)
    else:
        display = str(cmd)
    sys.stdout.write(f"[RUN] {display}\n")
    sys.stdout.flush()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=cwd,
        env=env,
    )
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
        proc.wait()
    finally:
        if proc.stdout:
            proc.stdout.close()
    if proc.returncode != 0:
        exit_with_error(f"Command failed ({proc.returncode}): {display}")
    sys.stdout.write(f"[OK] {display}\n")
    sys.stdout.flush()


def fetch_and_extract_package(
    package_path: str, workspace_run: str, udf_subdir: str = "udf"
) -> str:
    """
    Download package if s3://..., extract into workspace_run/udf_subdir (fresh),
    and return the absolute path to the udf folder.
    Supports formats accepted by shutil.unpack_archive (zip, tar, etc).
    """
    s3_conf = ensure_s3_conf()
    os.makedirs(workspace_run, exist_ok=True)

    # Prepare local archive path
    if package_path.startswith("s3://"):
        if not s3_conf:
            exit_with_error("S3 credentials required to download package from S3")
        try:
            local_dir = os.path.join(workspace_run, "package")
            os.makedirs(local_dir, exist_ok=True)
            logger.info(f"Downloading package from S3: {package_path} -> {local_dir}")
            local_file = download_from_s3(package_path, local_dir, s3_conf)
            logger.info(f"Downloaded package to {local_file}")
        except Exception as e:
            exit_with_error(f"Failed to download package from S3: {e}")
    else:
        local_file = os.path.expanduser(package_path)
        if not os.path.exists(local_file):
            exit_with_error(f"Package file not found: {local_file}")

    # Validate supported archive by suffix
    lower = local_file.lower()
    supported_suffixes = (
        ".zip",
        ".tar",
        ".tar.gz",
        ".tgz",
        ".tar.bz2",
        ".tbz2",
        ".tar.xz",
        ".txz",
    )
    if not any(lower.endswith(suf) for suf in supported_suffixes):
        exit_with_error(
            "Unsupported package format. Supported: zip, tar, tar.gz, tgz, tar.bz2, tar.xz"
        )

    # Extract into udf_path (fresh: remove existing to avoid stale files)
    udf_path = os.path.join(workspace_run, udf_subdir)
    if os.path.exists(udf_path):
        try:
            shutil.rmtree(udf_path)
        except Exception as e:
            exit_with_error(f"Failed to clear existing udf directory {udf_path}: {e}")
    os.makedirs(udf_path, exist_ok=True)

    try:
        logger.info(f"Extracting {local_file} -> {udf_path}")
        shutil.unpack_archive(local_file, udf_path)
    except Exception as e:
        exit_with_error(f"Failed to extract package {local_file}: {e}")

    logger.info(f"Package extracted to {udf_path}")
    return os.path.abspath(udf_path)
