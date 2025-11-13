import os, time
import subprocess
from scenedetect import open_video, ContentDetector, detect, split_video_ffmpeg
from loguru import logger
import cv2
from data_engine.core.base import BaseMapper
from data_engine.utils.log_utils import RayDataErrorLogger


def run_cmd(cmd):
    """运行命令，返回是否成功，及标准错误输出"""
    try:
        result = subprocess.run(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True
        )
        return True, result.stderr.decode("utf-8") + result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode("utf-8") + e.stdout.decode("utf-8")


class VideoMapperSplitByScene(BaseMapper):
    """
    视频场景切分
    对视频进行场景检测，并按场景裁剪为 mp4 格式视频片段（H.264 + AAC 编码），返回片段信息列表。
    输出字段
    scenes: 所有视频场景切分后的元信息字典列表#list
        path:视频切分后单个新视频路径#str
        scene:场景编号#int
        start:起始时间码#str或float
        start_sec:起始时间（秒）#float
        end:结束时间码#str或float
        end_sec:结束时间（秒）#float
        duration:场景持续时间（秒）#float
        start_frame:起始帧号#int
        end_frame:结束帧号#int
    """

    def __init__(
        self,
        clip_dir: str = None,
        duration: int = None,
        save_clips: bool = True,
        reserve_source_file: bool = True,
        threshold: int = 30,
        threads: int = 4,
        unique_column: str = "video_id",
        **kwargs,
    ):
        """
        初始化方法
        clip_dir: 视频片段保存目录 #用于指定场景切分后视频片段的保存路径
        duration: 最小场景时长（秒） #每个切分后的视频片段最少应满足的时长要求，单位为秒
        save_clips: 是否保存视频片段 #控制是否将切分后的视频片段保存到本地
        threshold: 场景变换判定阈值 #控制场景变化检测的灵敏度，值越小越敏感，单位为帧间像素差
        unique_column: 视频唯一标识对应的列名#视频唯一标识对应的列名
        """
        super().__init__(**kwargs)
        if save_clips:
            clip_dir = self.get_default_dir(clip_dir, "clip")

        self.min_duration = duration
        self.save_clips = save_clips
        self.clip_dir = clip_dir
        self.reserve_source_file = reserve_source_file
        self.threshold = threshold
        self.threads = threads
        self.unique_column = unique_column

        if self.save_clips:
            os.makedirs(self.clip_dir, exist_ok=True)

    def _process(self, data) -> list:
        """
        对视频进行场景检测，并按场景裁剪为 mp4 格式视频片段（H.264 + AAC 编码），返回片段信息列表。

        参数:
            data: 包含视频路径和 video_id_md5 等字段的字典。

        返回:
            scenes: 每个场景的元信息字典组成的列表，包含 start/end 时间、frame、duration 等字段。
        """
        file_path = data["path"].strip()
        unique_column = str(data[self.unique_column])

        # 1. 场景检测
        start = time.time()
        scene_list = detect(file_path, ContentDetector(threshold=self.threshold))
        take_time = time.time() - start
        scenes = []

        # 2. 创建输出目录（仅一次）
        if self.save_clips:
            clip_dir_path = os.path.join(self.clip_dir, unique_column)
            os.makedirs(clip_dir_path, exist_ok=True)

        # 3. 遍历每个场景
        end_sec = 0
        for i, scene in enumerate(scene_list):
            start_sec = scene[0].get_seconds()
            end_sec = scene[1].get_seconds()
            duration_sec = end_sec - start_sec

            # 忽略太短的场景
            if self.min_duration and duration_sec < self.min_duration:
                continue

            # 构建每段场景的描述字典
            scene_dict = {
                **data,
                "scene": i + 1,
                "start": scene[0].get_timecode(),
                "start_sec": start_sec,
                "end": scene[1].get_timecode(),
                "end_sec": end_sec,
                "duration": duration_sec,
                "start_frame": scene[0].get_frames(),
                "end_frame": scene[1].get_frames(),
            }

            # 4. 可选保存视频片段（统一为 mp4 + H.264/AAC）
            if self.save_clips:
                clip_filename = f"{i + 1}.mp4"
                clip_path = os.path.join(self.clip_dir, unique_column, clip_filename)
                cmd = cmd = [
                    "ffmpeg",
                    "-v",
                    "quiet",
                    "-nostdin",
                    "-y",
                    "-ss",
                    str(start_sec),
                    "-t",
                    str(end_sec - start_sec),
                    "-i",
                    file_path,
                    "-map",
                    "0:v:0",
                    "-map",
                    "0:a?",
                    "-map",
                    "0:s?",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-sn",
                    # "-threads", "5",
                ]
                if self.threads:
                    cmd.extend(["-threads", str(self.threads)])
                cmd.append(clip_path)
                success, _ = run_cmd(cmd)
                if not success:
                    data_error_directory = self._engine_config.get(
                        "data_error_directory"
                    )
                    if data_error_directory:
                        data_logger = RayDataErrorLogger(data_error_directory)
                        data_logger.log_error(
                            data, "split error", str(self.__class__.__name__)
                        )
                    continue

                scene_dict["path"] = clip_path
            scenes.append(scene_dict)

        # 5. 增加总场景数量字段
        scenes_cnt = len(scenes)
        for s in scenes:
            s["scenes_cnt"] = scenes_cnt
            s["video_duration"] = end_sec
        return scenes

    def process(self, data) -> list:
        file_path = data["path"]
        try:
            return self._process(data)
        except Exception as e:
            raise e
        finally:
            if not self.reserve_source_file and os.path.exists(file_path):
                os.remove(file_path)
