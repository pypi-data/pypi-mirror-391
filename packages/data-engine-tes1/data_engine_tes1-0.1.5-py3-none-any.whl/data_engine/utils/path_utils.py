import os


def get_workspace_run(workspace=None):
    workspace_run = os.environ.get("workspace_run") or os.path.join(
        workspace, "data-process-run"
    )
    return workspace_run


def get_udf(workspace=None):
    workspace = os.environ.get("workspace")
    workspace_run = get_workspace_run(workspace)
    udf_path = os.path.join(workspace_run, "udf")
    return udf_path


def download_udf(workspace, s3_conf, process_params):
    if not s3_conf:
        from data_engine.utils.path_utils import get_udf

        udf_path = get_udf(workspace)
        download_dir = os.path.join(udf_path, ".s3-download")
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
