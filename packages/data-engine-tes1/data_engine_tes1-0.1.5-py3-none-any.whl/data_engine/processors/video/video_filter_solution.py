# run_video_solution_filter.py

import sys
import argparse
import av  # PyAV库，用于读取视频元信息
import os
import shutil
from loguru import logger
from data_engine.core.base import BaseFilter


class VideoFilterSolution(BaseFilter):
    """
    分辨率过滤
    判断视频分辨率是否落在用户设定的最小/最大范围内
    输出字段
    solution#视频文件分辨率（宽度和高度）#[int,int]
    """

    def __init__(
        self,
        min_width: int = 1,
        max_width: int = 99999,
        min_height: int = 1,
        max_height: int = 99999,
        **kwargs,
    ):
        """
        初始化方法
        min_width: 最小视频宽度 # 允许通过的最小视频宽度（像素）
        max_width: 最大视频宽度 # 允许通过的最大视频宽度（像素）
        min_height: 最小视频高度 # 允许通过的最小视频高度（像素）
        max_height: 最大视频高度 # 允许通过的最大视频高度（像素）
        """
        super().__init__(**kwargs)
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def get_video_solution(self, video_path):
        with av.open(video_path) as container:
            stream = next(s for s in container.streams if s.type == "video")
            width = stream.codec_context.width
            height = stream.codec_context.height
            return width, height

    def process(self, row: dict) -> dict:
        video_path = row["path"]
        width, height = self.get_video_solution(video_path)
        row["solution"] = [width, height]
        if self.do_filter and not (
            self.min_width <= width <= self.max_width
            and self.min_height <= height <= self.max_height
        ):
            return {}
        return row
