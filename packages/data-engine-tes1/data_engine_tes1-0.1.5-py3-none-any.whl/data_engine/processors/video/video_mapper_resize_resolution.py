# resize_video_resolution.py

import os
import math
import shutil
import av
import ffmpeg
from loguru import logger
from data_engine.core.base import BaseMapper


class VideoMapperResizeResolution(BaseMapper):
    """
    批量处理视频分辨率
    根据用户设定的分辨率限制（最小/最大宽高）和比例调整策略，对输入视频进行分辨率校正。
    若原视频分辨率在允许范围内，则直接复制；
    若不满足限制，则按策略缩放后输出。

    1. 分辨率限制：
       - 视频宽高必须在 [min_width, max_width] × [min_height, max_height] 范围内。
       - 若原始尺寸超出范围，会按比例进行缩放。
       - 优先满足限制条件，其次保持原始宽高比（根据 aspect_mode）。

    2. 宽高比策略 (aspect_mode)：
       - "disable": 不强制保持原始宽高比，仅根据范围约束裁剪/缩放。
       - "increase": 允许扩大其中一边，使结果更接近原始宽高比（即保证画面不被压扁）。
       - "decrease": 允许缩小其中一边，使结果保持在约束范围内且比例更自然。

       举例说明：
       - 原视频比例为 16:9，max_width = 720，max_height = 720。
         - "disable": 直接缩放至 (720, 720)。
         - "increase": 调整为 (1280, 720)，以恢复 16:9 比例。
         - "decrease": 调整为 (720, 405)，以保持比例且不超界。

    输出字段
    path:处理后的新视频路径#str
    source_path:源视频路径#str
    """

    def __init__(
        self,
        min_width: int = 1,
        max_width: int = 4096,
        min_height: int = 1,
        max_height: int = 4096,
        aspect_mode: str = "disable",
        force_divisible_by: int = 1,
        file_out_path: str = None,
        **kwargs,
    ):
        """
        初始化方法
        min_width: 最小宽度 # 允许的最小视频宽度（像素）
        max_width: 最大宽度 # 允许的最大视频宽度（像素）
        min_height: 最小高度 # 允许的最小视频高度（像素）
        max_height: 最大高度 # 允许的最大视频高度（像素）
        aspect_mode: 策略 #['disable', 'decrease', 'increase'] # 宽高比调整策略
        file_out_path: 输出目录 # 输出目录路径
        """
        super().__init__(**kwargs)
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.aspect_mode = aspect_mode
        self.force_divisible_by = force_divisible_by
        self.file_out_path = self.get_default_dir(file_out_path)

    def get_video_resolution(self, video_path):
        with av.open(video_path) as container:
            container = av.open(video_path)
            stream = next(s for s in container.streams if s.type == "video")
            width = stream.codec_context.width
            height = stream.codec_context.height
            return width, height

    def compute_target_resolution(self, width, height):
        orig_ratio = width / height
        min_w, max_w = self.min_width, self.max_width
        min_h, max_h = self.min_height, self.max_height
        aspect_mode = self.aspect_mode
        force_divisible_by = self.force_divisible_by
        if width < min_w:
            height = min_w / orig_ratio
            width = min_w
        if width > max_w:
            height = max_w / orig_ratio
            width = max_w
        if height < min_h:
            width = min_h * orig_ratio
            height = min_h
        if height > max_h:
            width = max_h * orig_ratio
            height = max_h
        width = max(width, min_w)
        width = math.ceil(width / force_divisible_by) * force_divisible_by
        width = min(width, max_w)
        height = max(height, min_h)
        height = math.ceil(height / force_divisible_by) * force_divisible_by
        height = min(height, max_h)
        if aspect_mode == "increase":
            if width / height < orig_ratio:
                width = height * orig_ratio
            else:
                height = width / orig_ratio
        elif aspect_mode == "decrease":
            if width / height < orig_ratio:
                height = width / orig_ratio
            else:
                width = height * orig_ratio
        width = int(round(width / force_divisible_by)) * force_divisible_by
        height = int(round(height / force_divisible_by)) * force_divisible_by
        return int(width), int(height)

    def resize_video(self, video_path, output_path, width, height):
        args = ["-nostdin", "-v", "error", "-y"]
        stream = ffmpeg.input(video_path)
        stream = stream.filter("scale", width // 2 * 2, height=height // 2 * 2)
        stream = stream.output(output_path).global_args(*args)
        stream.run(capture_stdout=True, capture_stderr=True)
        logger.info(f"Resized video saved to: {output_path}")

    def process(self, row: dict) -> dict:
        video_path = row["path"]
        logger.info(f"video_mapper_resize_resolution start process {video_path}")
        width, height = self.get_video_resolution(video_path)
        target_w, target_h = self.compute_target_resolution(width, height)
        base_name = os.path.basename(video_path)
        output_path = os.path.join(self.file_out_path, base_name)
        if (target_w, target_h) == (width, height):
            shutil.copy2(video_path, output_path)
        else:
            self.resize_video(video_path, output_path, target_w, target_h)
        row["path"] = output_path
        row["source_path"] = video_path
        logger.info(f"video_mapper_resize_resolution success process {video_path}")
        return row


# python resize_video_resolution.py \
#   --video_path input.mp4 \
#   --output_path resized.mp4 \
#   --min_width 256 --max_width 1920 \
#   --min_height 256 --max_height 1080 \
#   --aspect_mode decrease \
#   --force_divisible_by 2
