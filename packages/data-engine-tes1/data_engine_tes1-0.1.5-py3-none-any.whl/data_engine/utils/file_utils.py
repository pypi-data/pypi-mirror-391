import os


def safe_makedirs(path, exist_ok=True):
    """
    安全创建目录，兼容 path 为目录路径或文件路径的情况。

    如果 path 是目录路径，则直接创建该目录；
    如果 path 是文件路径，则仅创建其父目录。
    """
    if os.path.splitext(path)[1]:  # 有文件扩展名，视为文件路径
        dir_path = os.path.dirname(path) or "."
    else:  # 无扩展名，视为目录路径
        dir_path = path

    os.makedirs(dir_path, exist_ok=exist_ok)
