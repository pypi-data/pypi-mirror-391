import os
import librosa
import soundfile as sf
from loguru import logger
from data_engine.core.base import BaseMapper


class AudioMapperTimestampSegmenter(BaseMapper):
    """
    音频按照时间切分
    从长音频中按照给定的起止时间（start、end）提取音频片段
    """

    def __init__(self, file_out_path: str = None, file_path: str = "path", **kwargs):
        """
        初始化方法
        file_out_path: 输出根路径 # 用于保存截取后的音频片段；未指定时使用默认工作目录
        file_path: 音频文件字段名称#用于加载音频文件
        """
        super().__init__(**kwargs)
        self.file_out_path = self.get_default_dir(file_out_path)
        os.makedirs(self.file_out_path, exist_ok=True)
        self.file_path = file_path

    def process(self, row: dict) -> dict:
        audio_path = row[self.file_path]
        start_time = row["start"]
        end_time = row["end"]

        # Load audio file
        y, sr = librosa.load(audio_path, sr=None)
        # Convert start and end times to samples
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)

        # Ensure the segment is within the audio bounds
        if start_sample < 0 or end_sample > len(y) or start_sample >= end_sample:
            logger.warning(
                f"Invalid segment times for {audio_path}: start={start_time}, end={end_time}. len={len(y)/sr:.2f}s"
            )
            row[self.file_path] = None
            row["source_path"] = audio_path
            return row

        # Extract the segment
        segmented_audio = y[start_sample:end_sample]

        # Determine output directory and file name
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_dir = os.path.join(self.file_out_path, base_name)
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename for the segment
        segment_filename = f"{base_name}_{start_time:.2f}_{end_time:.2f}.wav"
        output_filepath = os.path.join(output_dir, segment_filename)

        # Save the segmented audio
        sf.write(output_filepath, segmented_audio, sr)
        logger.info(f"Saved segmented audio to: {output_filepath}")
        row[self.file_path] = output_filepath
        row["source_path"] = audio_path
        return row
