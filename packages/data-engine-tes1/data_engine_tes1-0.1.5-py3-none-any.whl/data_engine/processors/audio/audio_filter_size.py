import os
import shutil
from loguru import logger
from data_engine.core.base import BaseFilter


def size_to_bytes(size_str: str) -> int:
    """Convert size like '5MB' or '100kb' to bytes."""
    size_str = str(size_str).strip().upper()
    units = {
        "TB": 1024**4,
        "GB": 1024**3,
        "MB": 1024**2,
        "KB": 1024,
        "B": 1,
    }
    for unit in sorted(units.keys(), key=len, reverse=True):
        if size_str.endswith(unit):
            return int(float(size_str.replace(unit, "").strip()) * units[unit])
    return int(size_str)


class AudioFilterSize(BaseFilter):
    """
    根据音频文件大小打标签过滤
    判断音频文件大小是否落在用户设定的最小/最大范围内
    """

    def __init__(
        self,
        min_size: str = "0B",
        max_size: str = "1TB",
        file_path: str = "path",
        **kwargs,
    ):
        """
        初始化方法
        min_size: 最小文件大小 # 最小音频文件大小，支持B、KB、MB、GB、TB
        max_size: 最大文件大小 # 最大音频文件大小，支持B、KB、MB、GB、TB
        """
        super().__init__(**kwargs)
        self.min_bytes = size_to_bytes(min_size)
        self.max_bytes = size_to_bytes(max_size)
        self.file_path = file_path

    def get_file_size(self, file_path):
        return os.path.getsize(file_path)

    def process(self, row: dict) -> dict:
        audio_path = row[self.file_path]
        size = self.get_file_size(audio_path)
        row["size"] = size
        if self.do_filter and not (self.min_bytes <= size <= self.max_bytes):
            return {}
        return row
