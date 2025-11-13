import os
import copy
import subprocess
import math
from loguru import logger
from data_engine.core.base import BaseMapper


def get_video_duration(video_path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)


def cut_video(input_path, output_path, start_time, duration=None):
    cmd = [
        "ffmpeg",
        "-ss",
        str(start_time),
        "-i",
        input_path,
    ]
    if duration is not None:
        cmd += ["-t", str(duration)]

    cmd += [
        "-c",
        "copy",
        "-y",
        output_path,
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def split_video_by_duration(
    input_path, output_dir, split_duration=10, min_last_split_duration=0
):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    total_duration = get_video_duration(input_path)
    num_splits = math.floor(total_duration / split_duration)
    split_paths = []
    for i in range(num_splits):
        start = i * split_duration
        output_path = os.path.join(output_dir, f"{base_name}_part{i}.mp4")
        cut_video(input_path, output_path, start, split_duration)
        split_paths.append(output_path)
    last_start = num_splits * split_duration
    last_duration = total_duration - last_start
    if last_duration >= min_last_split_duration:
        output_path = os.path.join(output_dir, f"{base_name}_part{num_splits}.mp4")
        cut_video(input_path, output_path, last_start)
        split_paths.append(output_path)
    return split_paths


class VideoMapperFixedDurationSegmenter(BaseMapper):
    """
    按照持续时间对视频进行切分
    按固定时长切割视频，返回分段后的视频路径列表。
    输出字段
    data:切分后的视频list#[
        path:切分后的新视频绝对路径#str
        source_path:源视频绝对路径#str
    ]
    """

    def __init__(
        self,
        split_duration: int = 10,
        min_last_split_duration: int = 3,
        file_out_path: str = None,
        **kwargs,
    ):
        """
        初始化方法。
        split_duration: 切割时长 # 切割的持续时间(s)，按照该时间对视频进行切分
        min_last_split_duration: 最小切割时长 # 允许的最小切割时长(s)，如果最后一段小于该时长，则不保留
        file_out_path: 输出根目录 # 输出根目录。如果未指定，会创建默认路径
        """
        super().__init__(**kwargs)
        self.split_duration = split_duration
        self.min_last_split_duration = min_last_split_duration
        self.file_out_path = self.get_default_dir(file_out_path)
        os.makedirs(self.file_out_path, exist_ok=True)

    def process(self, row: dict) -> list:
        video_path = row.get("path")

        segment_paths = split_video_by_duration(
            input_path=video_path,
            output_dir=self.file_out_path,
            split_duration=self.split_duration,
            min_last_split_duration=self.min_last_split_duration,
        )
        result = []
        for p in segment_paths:
            d = copy.deepcopy(row)
            d["path"] = p
            d["source_path"] = video_path
            result.append(d)
        return result
