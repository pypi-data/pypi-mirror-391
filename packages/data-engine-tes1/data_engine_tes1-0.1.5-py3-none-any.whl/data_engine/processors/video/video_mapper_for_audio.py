# extract_audio_from_video.py

import os
import av
import numpy as np
import soundfile as sf
from loguru import logger
from data_engine.core.base import BaseMapper


class VideoMapperForAudio(BaseMapper):
    """
    视频转音频处理器。
    从输入的 JSONL 数据中读取视频路径，提取音频流，
    并将原有 'path' 字段替换为生成的音频文件路径，原视频路径保存在 source_path 字段。
    输出字段
    path:视频转音频后的绝对路径，.wav 文件保存该目录#str
    source_path:来源视频绝对路径#str
    """

    def __init__(self, file_out_path: str = None, **kwargs):
        """
        初始化方法。
        file_out_path: 输出根目录 # 音频文件输出根目录。如果未指定，会创建默认路径
        """
        super().__init__(**kwargs)
        self.file_out_path = self.get_default_dir(file_out_path)

    def process(self, data: dict) -> dict:
        """
        处理单个视频文件，提取音频并保存，将 'path' 字段改为新的音频路径，原视频路径保存在 source_path。
        :param data: 包含 'path' 键的视频路径字典
        :return: 更新后的字典，'path' 字段指向生成的 .wav 文件，source_path为原视频路径，出错或无音频时设为None
        """
        video_path = data["path"]
        # 构造输出子目录和文件名
        base = os.path.splitext(os.path.basename(video_path))[0]
        subdir = os.path.join(self.file_out_path, base)
        os.makedirs(subdir, exist_ok=True)
        output_audio_path = os.path.join(subdir, f"{base}.wav")

        # 提取音频帧
        with av.open(video_path) as container:
            audio_streams = [s for s in container.streams.audio]
            stream0 = audio_streams[0]
            stream0.thread_type = "AUTO"
            frames = []
            for frame in container.decode(audio=0):
                arr = frame.to_ndarray()
                if arr.ndim == 2:
                    arr = arr[0]
                frames.append(arr)
        # 拼接并保存
        audio = np.concatenate(frames)
        sr = stream0.rate
        sf.write(output_audio_path, audio, sr, subtype="PCM_16")
        data["path"] = output_audio_path
        data["source_path"] = video_path
        return data
