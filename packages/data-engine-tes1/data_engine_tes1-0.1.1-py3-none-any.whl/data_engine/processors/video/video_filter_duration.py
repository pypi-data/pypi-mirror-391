# run_video_duration_filter.py

import sys
import argparse
import av  # PyAV库，用于读取视频元信息
import os
import shutil
from loguru import logger
from data_engine.core.base import BaseFilter


class VideoFilterDuration(BaseFilter):
    """
    按照视频的持续时间进行过滤
    判断视频时长是否落在用户设定的最小/最大范围内
    输出字段
    path: 源视频绝对路径#str
    duration: 视频时长（秒）#float
    """

    def __init__(
        self,
        min_duration: float = 0.0,
        max_duration: float = None,
        file_path: str = "path",
        **kwargs,
    ):
        """
        初始化方法
        min_duration: 最小长度 # 允许通过的最小视频时长(s)
        max_duration: 最大长度 # 允许通过的最大视频时长(s)
        file_path: 视频文件字段名称#用于加载来源视频，默认值字段名称：path
        """
        super().__init__(**kwargs)
        self.min_duration = min_duration
        self.max_duration = max_duration or float("inf")
        self.file_path = file_path

    def get_video_duration(self, video_path):
        with av.open(video_path) as container:
            stream = next(s for s in container.streams if s.type == "video")
            if stream is None:
                logger.warning(f"No video stream found in {video_path}")
                return 0.0

            # 1. 优先从视频流获取时长
            if stream.duration is not None:
                logger.warning(f"fetch duration for video: {video_path}")
                duration = float(stream.duration * stream.time_base)
                return duration
            # 2. 若视频流无时长，尝试从容器获取总时长
            if container.duration is not None:
                # container.duration 的单位是微秒（μs），转换为秒
                duration = container.duration / 1_000_000
                logger.info(
                    f"Got duration from container for {video_path}: {duration}s"
                )
                return duration

            # 3. 所有方式都无法获取时长
            logger.warning(
                f"Both stream and container have no duration for {video_path}"
            )
            return 0.0
            # duration = float(stream.duration * stream.time_base)
            # return duration

    def process(self, row: dict) -> dict:
        # video_path = row["path"]
        video_path = row[self.file_path]
        duration = self.get_video_duration(video_path)
        row["duration"] = duration
        if self.do_filter and not (self.min_duration <= duration <= self.max_duration):
            return {}
        return row
