#!/usr/bin/env python3
# audio_duration_filter.py

import os
import shutil
from loguru import logger
import librosa
from data_engine.core.base import BaseFilter


class AudioFilterDuration(BaseFilter):
    """
    音频时长打标过滤
    判断音频文件时长是否落在用户设定的最小/最大范围内
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
        min_duration: 最小时长 # 最小音频时长，单位是（秒）
        max_duration: 最大时长 # 最大音频时长，单位是（秒）
        file_path: 音频文件字段名称#用于加载音频文件
        """
        super().__init__(**kwargs)
        self.min_duration = min_duration
        self.max_duration = max_duration or float("inf")
        self.file_path = file_path

    def get_audio_duration(self, audio_path):
        return librosa.get_duration(path=audio_path)

    def process(self, row: dict) -> dict:
        audio_path = row[self.file_path]
        duration = self.get_audio_duration(audio_path)
        row["duration"] = duration
        if self.do_filter and not (self.min_duration <= duration <= self.max_duration):
            return {}
        return row
