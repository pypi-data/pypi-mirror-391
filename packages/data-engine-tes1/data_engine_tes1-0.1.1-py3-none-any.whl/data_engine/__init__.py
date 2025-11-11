from importlib.metadata import version, PackageNotFoundError
import shutil

try:
    __version__ = version("data_engine")  # 这里是__version__（双下划线）
except PackageNotFoundError:
    __version__ = "unknown"