import os
import ffmpeg
from loguru import logger
from data_engine.core.base import BaseMapper


def apply_ffmpeg_filter(
    input_path, output_path, filter_name, filter_kwargs, overwrite_output=True
):
    """应用FFmpeg滤镜到视频文件"""

    stream = (
        ffmpeg.input(input_path)
        .filter(filter_name, **filter_kwargs)
        .output(output_path)
    )

    if overwrite_output:
        stream = stream.overwrite_output()

    stream.run(capture_stderr=True, quiet=True)


def parse_filter_kwargs(kwargs_dict):
    """将字典形式的参数转换为适合ffmpeg的格式"""
    result = {}
    for key, value in kwargs_dict.items():
        try:
            if isinstance(value, str) and value.isdigit():
                result[key] = int(value)
            elif isinstance(value, str) and value.replace(".", "").isdigit():
                result[key] = float(value)
            else:
                result[key] = value
        except:
            result[key] = value
    return result


class VideoMapperFfmpegPackage(BaseMapper):
    """
    Ffmpeg包装器
    为每条视频数据应用指定的 FFmpeg 滤镜，并将处理后的视频保存为新文件。
    一对一输出：`path` 为新视频路径，`source_path` 保存原始视频路径。
    输出字段
    path:Ffmpeg滤镜视频绝对路径，滤镜视频在该目录#str
    source_path:原始视频绝对路径，原始视频在该目录#str
    """

    def __init__(
        self,
        filter_name: str,
        filter_kwargs: dict = None,
        output_dir: str = None,
        output_suffix: str = None,
        **kwargs,
    ):
        """
        初始化方法
        filter_name: FFmpeg名称 # 需要应用的滤镜名称，如 "boxblur"、"crop"、"scale"、"hue" 等
        filter_kwargs: FFmpeg参数 # 滤镜参数字典，例如 {"luma_radius":"5", "luma_power":"1.0"}
        output_dir: 输出目录 # 若为空，则默认工作目录下的类名目录
        output_suffix: 输出后缀 # 若为空，默认为 _{filter_name}
        """
        super().__init__(**kwargs)
        self.filter_name = filter_name
        self.filter_kwargs = filter_kwargs or {}
        self.output_dir = self.get_default_dir(output_dir)
        self.output_suffix = output_suffix or f"_{filter_name}"

    def process(self, row: dict) -> dict:
        """处理单行数据：应用 FFmpeg 滤镜并输出新路径"""
        video_path = row.get("path")
        if not video_path:
            logger.warning(f"Skipping row due to missing path: {row}")
            return {**row, "path": None, "source_path": None}

        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}{self.output_suffix}{ext}"
        output_path = os.path.join(self.output_dir, output_filename)
        os.makedirs(self.output_dir, exist_ok=True)

        parsed_kwargs = parse_filter_kwargs(self.filter_kwargs)
        logger.info(f"video_mapper_ffmpeg_package mideler process {output_path}")

        try:
            apply_ffmpeg_filter(
                input_path=video_path,
                output_path=output_path,
                filter_name=self.filter_name,
                filter_kwargs=parsed_kwargs,
            )
            logger.info(f"video_mapper_ffmpeg_package success process {output_path}")
        except Exception as e:
            logger.error(f"FFmpeg filter apply failed for {video_path}: {e}")
            return {**row, "path": None, "source_path": video_path}

        d = {**row}
        d["source_path"] = video_path
        d["path"] = output_path
        return d
