# fixed_duration_segmenter.py
import os
import librosa
import soundfile as sf
import json
import math
from loguru import logger
from data_engine.core.base import BaseMapper


class AudioMapperFixedDurationSegmenter(BaseMapper):
    """
    固定时长音频分段处理器
    从输入的 JSONL 数据中读取音频路径，对每个音频文件进行分段，
    并将分段后的音频路径添加到输出元数据中。
    """

    def __init__(
        self,
        segment_duration: float = 5.0,
        file_out_path: str = None,
        file_path: str = "path",
        **kwargs,
    ):
        """
        初始化方法
        segment_duration: 持续时间 # 每个音频片段的时长
        file_out_path: 输出路径 # 分段音频文件的输出根目录
        """
        super().__init__(**kwargs)
        self.segment_duration = segment_duration
        self.file_out_path = self.get_default_dir(file_out_path)
        self.file_path = file_path

    def process(self, data: dict) -> list:
        """
        处理单个音频文件，返回分段后的多条记录列表。
        输入示例: {'path': '/path/to/audio.m4a', ...}
        输出示例: [
            {'path': '/out/dir/audio/audio_0s.wav', 'source_path': '/path/to/audio.m4a', ...},
            {'path': '/out/dir/audio/audio_5s.wav', 'source_path': '/path/to/audio.m4a', ...},
            ...
        ]
        若发生错误或没有生成分段，返回空列表 []（而不是 None）。
        """
        audio_path = data[self.file_path]  # 从 'path' 字段获取音频路径
        segmented_audio_paths = []
        y, sr = librosa.load(audio_path, sr=None)
        logger.info(f"Loaded audio: {audio_path}, shape: {y.shape}, sample rate: {sr}")
        total_samples = len(y)
        if sr <= 0 or total_samples == 0:
            logger.warning(
                f"AudioMapperFixedDurationSegmenter: empty or invalid audio: {audio_path}"
            )
            return []
        segment_samples = int(math.floor(self.segment_duration * sr))
        if segment_samples <= 0:
            logger.error(
                f"AudioMapperFixedDurationSegmenter: invalid segment_samples computed: {segment_samples}"
            )
            return []
        logger.info(
            f"Total samples: {total_samples}, segment duration: {self.segment_duration}s, segment samples: {segment_samples}"
        )
        # 获取原始文件名（不带扩展名）
        original_basename = os.path.splitext(os.path.basename(audio_path))[0]
        # 为当前音频文件创建子目录
        output_sub_dir = os.path.join(self.file_out_path, original_basename)
        os.makedirs(output_sub_dir, exist_ok=True)
        out_records = []
        # iterate by sample offsets
        for start_sample in range(0, total_samples, segment_samples):
            end_sample = start_sample + segment_samples
            segment = y[start_sample:end_sample]
            # 如果最后一段不够长度，跳过
            if len(segment) < segment_samples:
                logger.warning(
                    f"AudioMapperFixedDurationSegmenter: skipping incomplete segment for {audio_path} at offset {start_sample}, length {len(segment)} samples"
                )
                break
            start_sec = int(start_sample / sr)
            segment_filename = f"{original_basename}_{start_sec}s.wav"
            output_full_path = os.path.join(output_sub_dir, segment_filename)
            sf.write(output_full_path, segment, sr)
            # 深拷贝原输入数据并替换 path/source_path 字段
            out_row = dict(data)
            # out_row["path"] = output_full_path
            out_row[self.file_path] = output_full_path
            out_row["source_path"] = audio_path
            # 可选：记录每段的开始时间/时长/采样数
            out_row["segment_start_sec"] = float(start_sec)
            out_row["segment_duration_sec"] = float(self.segment_duration)
            out_row["segment_samples"] = int(len(segment))
            out_records.append(out_row)
        logger.info(
            f"AudioMapperFixedDurationSegmenter: segmented {audio_path} into {len(out_records)} segments."
        )
        return out_records
