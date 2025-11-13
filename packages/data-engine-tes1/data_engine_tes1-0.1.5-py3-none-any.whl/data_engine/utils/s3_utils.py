import os, re
import s3fs
from typing import List
from filelock import FileLock
from loguru import logger


def download_from_s3(
    s3_path: str, local_path: str, s3_conf: dict = None, use_cache=True
):
    """
    从 S3 下载文件或文件夹到本地目录，使用文件锁保证分布式环境下安全执行。

    参数:
        s3_path (str): S3 路径，例如 'my-bucket/my-folder' 或 'my-bucket/my-file.txt'
        local_path (str): 下载到本地的路径
        s3_conf (dict): 可选，用于 boto3 的 client_kwargs
        s3_url_style (str): addressing_style，默认为 'path'

    示例:
        download_from_s3('my-bucket/data', './local_data')
        download_from_s3('my-bucket/file.txt', './file.txt')
    """
    # 创建文件锁，保证多进程/多节点不重复拉取
    s3_path = re.sub(r"^(s3|ks3)://", "", s3_path)
    s3_path = s3_path.strip("/")
    file_name = os.path.basename(s3_path)
    result = os.path.join(local_path, file_name)
    logger.info(f"download {s3_path}   {result}")
    lock_path = result + ".lock"
    # with FileLock(lock_path):

    # if os.path.exists(result):
    #     # 已经存在则跳过下载，适合缓存拉取
    #     return result
    s3_url_style = s3_conf.pop("style", None) or os.environ.get("S3_URL_STYLE", "auto")
    fs = s3fs.S3FileSystem(
        anon=False,
        use_ssl=False,
        client_kwargs=s3_conf or {},
        config_kwargs={
            "s3": {"addressing_style": s3_url_style},
            "connect_timeout": 10,
            "read_timeout": 300,
        },
    )

    def download_file(source, dest):
        if use_cache and os.path.exists(dest):
            return
        fs.get(source, dest)

    # 判断是文件还是目录
    if fs.isfile(s3_path):
        os.makedirs(os.path.dirname(result), exist_ok=True)
        fs.get(s3_path, result)
        return result
    elif fs.isdir(s3_path):
        if not s3_path.endswith("/"):
            s3_path += "/"
        files = fs.find(s3_path, detail=True)
        download_list = []
        for full_s3_path in files:
            relative_path = full_s3_path[len(s3_path) :]
            target_local_path = os.path.join(result, relative_path)
            os.makedirs(os.path.dirname(target_local_path), exist_ok=True)
            download_list.append((full_s3_path, target_local_path))
        try:
            import ray

            in_ray_cluster = ray.is_initialized()
            if not in_ray_cluster:
                raise RuntimeError("no in ray cluster")
            results = []
            pending = []

            for task in download_list:
                # 提交一个远程任务
                pending.append(ray.remote(download_file).remote(task[0], task[1]))

                # 当达到最大并发数时，等待至少一个任务完成
                if len(pending) >= 50:
                    done, pending = ray.wait(pending, num_returns=1)
                    # 获取完成任务的结果
                    results.append(ray.get(done[0]))

            # 收尾：等待所有剩余任务完成
            if pending:
                results.extend(ray.get(pending))
        except Exception as e:
            for task in download_list:
                download_file(task[0], task[1])

        return result
    else:
        raise FileNotFoundError(f"S3 路径不存在: {s3_path}")


def list_s3_contents(s3_path: str, s3_conf: dict = None) -> List[str]:
    """
    列出 S3 路径下的所有内容（文件和子文件夹）。

    参数:
        s3_path (str): 例如 'my-bucket/my-folder'
        s3_conf (dict): 可选的 S3 配置参数，如 {'key': 'xxx', 'secret': 'yyy', 'client_kwargs': {'region_name': 'ap-northeast-1'}}

    返回:
        List[str]: 所有内容的完整 S3 路径列表
    """
    s3_url_style = s3_conf.get("style", None) or os.environ.get("S3_URL_STYLE", "auto")
    fs = s3fs.S3FileSystem(
        anon=False,
        use_ssl=False,
        client_kwargs=s3_conf,
        config_kwargs={
            "s3": {"addressing_style": s3_url_style},
            "connect_timeout": 10,
            "read_timeout": 300,
        },
    )
    if not s3_path.endswith("/"):
        s3_path += "/"
    try:
        contents = fs.ls(s3_path)
        return contents
    except FileNotFoundError:
        print(f"路径不存在: {s3_path}")
        return []
