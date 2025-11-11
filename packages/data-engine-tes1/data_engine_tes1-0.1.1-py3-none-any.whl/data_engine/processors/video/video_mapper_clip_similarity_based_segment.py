import os
from data_engine.core.base import BaseFilter
import torch
import numpy as np
from loguru import logger
from tqdm import tqdm
import av
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images
from scenedetect.video_splitter import split_video_ffmpeg
from pathlib import Path
import os
import hashlib
from transformers import CLIPProcessor, CLIPModel
import copy
from data_engine.utils.model_utils import get_model_path

import imagebind
from imagebind import data
from imagebind.models import imagebind_model
from imagebind.models.imagebind_model import ModalityType


class VideoMapperClipSimilarityBasedSegment(BaseFilter):
    """
    基于相似度的视频切片、分割
    通过计算帧的相似度构建有足够视觉区别但是场景一致的视频切片序列
    交错视频工作流专用算法
    交错视频所有的中间结果目录需要设置为相同的目录
    """

    use_class = True

    def __init__(
        self,
        threshold_upper: float = 0.8,
        threshold_lower: float = 0.6,
        middel_result_save_dir: str = "middle_result",
        **kwargs,
    ):
        """
        初始化方法
        middel_result_save_dir: 中间结果存储目录#中间结果存储目录
        threshold_upper: 相似度上阈值#相似度上阈值，大于此值的片段将直接略过
        threshold_lower: 相似度下阈值#相似度下阈值，小于此值的片段意味着启动新序列
        """
        super().__init__(**kwargs)
        self.model = None  # 模型与预处理器将在首次使用时懒加载
        self.threshold_upper = threshold_upper
        self.threshold_lower = threshold_lower
        middel_result_save_dir = self.get_default_dir(middel_result_save_dir, "segment")
        self.middel_result_save_dir = middel_result_save_dir
        self.device = None

    def cosine_similarity_between_embeddings(self, emb1, emb2):
        """
        计算两个特征向量之间的余弦相似度
        参数:
            emb1: 第一个特征向量（Tensor，shape: [D]）
            emb2: 第二个特征向量（Tensor，shape: [D]）
        返回:
            相似度标量（float），取值范围[-1,1]
        """
        # 将 GPU 上的张量转成 CPU 上 NumPy 数组，并调整为二维 shape 以适配 cosine_similarity 接口
        emb1 = emb1.cpu().numpy().reshape(1, -1)
        emb2 = emb2.cpu().numpy().reshape(1, -1)
        # 调用 sklearn 的 cosine_similarity，返回二维数组，所以取第一个元素
        return cosine_similarity(emb1, emb2)[0][0]

    def calculate_similarity(self, embeddings):
        """
        计算相邻特征向量之间的相似度序列
        参数:
            embeddings: 按顺序堆叠好的特征向量（Tensor），shape: [N, D]
        返回:
            相邻片段之间相似度的列表，例如长度为 N-1
        """
        similarities = []
        # 遍历相邻特征向量对
        for i in range(len(embeddings) - 1):
            similarity = self.cosine_similarity_between_embeddings(
                embeddings[i], embeddings[i + 1]
            )
            similarities.append(float(similarity))
        return similarities

    def extract_frames_uniformly(self, clip_path, num_frames=3):
        """
        将视频划分为 num_frames 段，从每段中间抽取一帧，返回 PIL.Image 列表。
        不保存帧到磁盘，仅返回图像对象。
        """
        container = av.open(clip_path)
        stream = container.streams.video[0]
        total_frames = stream.frames

        if total_frames <= 0:
            print(f"Warning: Cannot get frame count for {clip_path}, skipping.")
            return []

        # 每段取中间位置的帧索引
        split_size = total_frames / (num_frames + 1)
        indices = [int(split_size * (i + 1)) for i in range(num_frames)]

        frames = []
        for i, frame in enumerate(container.decode(stream)):
            if i in indices:
                img = frame.to_image()
                frames.append(img)
            if i > max(indices):
                break

        return frames

    def save_horizontal_concat(
        self, frames, frame_dir_base, video_path, video_path_md5_hash, pad=10
    ):
        """
        横向拼接每组图像，图像间隔 pad 像素，并保存为图片。

        Args:
            frames: List[List[PIL.Image]]
            frame_dir_base: 保存目录
            pad: 每张图之间的 padding，单位像素

        Returns:
            frame_paths: List[str] 保存的图片路径列表

        """

        video_path = Path(video_path)
        frame_dir_base = Path(frame_dir_base)

        video_name = video_path_md5_hash  # 不带后缀的文件名
        save_dir = frame_dir_base / video_name

        os.makedirs(save_dir, exist_ok=True)
        frame_paths = []

        num_frames = len(frames)
        # 当前数据中最后一帧的编号是 num_frames，计算它需要几位
        digits = max(4, len(str(num_frames)))  # 至少 4 位，不够再扩展

        for i, imgs in enumerate(frames):
            widths, heights = zip(*(img.size for img in imgs))
            total_width = sum(widths) + pad * (len(imgs) - 1)
            max_height = max(heights)

            new_img = Image.new("RGB", (total_width, max_height), color=(255, 255, 255))
            x_offset = 0
            for img in imgs:
                new_img.paste(img, (x_offset, 0))
                x_offset += img.size[0] + pad

            filename = f"video_frames_{i+1:0{digits}d}.jpg"  # 按计算得到的 digits 补零
            save_path = os.path.join(save_dir, filename)
            new_img.save(save_path)
            frame_paths.append(save_path)

        return frame_paths

    def find_subsequences_with_conditions(self, lst, max_gap=5, min_length=2):
        """
        按照相邻文件编号间隔划分序列，返回所有符合条件的子序列
        参数:
            lst: 包含文件路径的列表（如 '.../123_xxx' 格式），需要根据文件名中数字排序后的连续性切分
            max_gap: 相邻文件编号之间允许的最大间隔（默认 5），超过则视为分段
            min_length: 子序列最短长度（默认 2），长度小于该值的子序列丢弃
        返回:
            subsequences: 按条件筛选后的子序列列表
        """
        subsequences = []  # 用来存储符合条件的子序列

        if len(lst) == 0:
            return []  # 空列表直接返回空结果

        # 初始化当前子序列，以第一个元素开始
        current_subseq = [lst[0]]

        # 遍历从第二个元素开始的列表
        for i in range(1, len(lst)):
            # 从路径中提取文件编号部分，假设文件路径中编号在文件名中，按 split('_')[0] 获取

            current_value = int(lst[i].split("-")[-1].replace(".mp4", ""))
            prev_value = int(lst[i - 1].split("-")[-1].replace(".mp4", ""))

            # 判断当前编号与前一个编号之间的差值是否在 max_gap 范围内
            if current_value - prev_value <= max_gap:
                # 差值小于等于 max_gap，则继续添加到当前子序列
                if len(current_subseq) < 10:
                    current_subseq.append(lst[i])
                else:
                    # 当前子序列长度已达上限（10），先将其添加到结果中，然后从当前元素重新开始新序列
                    subsequences.append(current_subseq)
                    current_subseq = [lst[i]]
            else:
                # 当前编号与前一编号之间差值大于 max_gap，结束当前子序列
                # 只有当子序列长度大于等于 min_length 时，才添加进结果
                if len(current_subseq) >= min_length:
                    subsequences.append(current_subseq)
                # 开始新的子序列
                current_subseq = [lst[i]]

        # 遍历结束后，还需检查最后一条子序列
        if len(current_subseq) >= min_length:
            subsequences.append(current_subseq)

        return subsequences

    def split_video_by_content(
        self, video_path, clip_dir_base, video_path_md5_hash, threshold=3.0
    ):
        """
        使用 PySceneDetect 对视频进行内容分割，并保存为多个 clip 文件。

        参数:
            video_path: 原始视频路径
            clip_dir: 保存 clip 的目录
            threshold: 内容变化检测阈值（默认 30.0）

        返回:
            clip_path_list: 所有分割后视频片段的路径列表
        """
        video_path = Path(video_path)
        clip_dir_base = Path(clip_dir_base)

        video_name = video_path_md5_hash  # 不带后缀的文件名
        clip_dir = clip_dir_base / video_name
        clip_dir.mkdir(parents=True, exist_ok=True)

        video_manager = VideoManager([str(video_path)])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))

        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)

        scene_list = scene_manager.get_scene_list()
        print(f"[INFO] {len(scene_list)} scenes detected.")

        # 保存 clip
        split_video_ffmpeg(
            [str(video_path)], scene_list, output_dir=str(clip_dir), show_progress=True
        )

        # 获取所有输出的 clip 路径
        clip_path_list = sorted(str(p) for p in clip_dir.glob("*.mp4"))

        return clip_path_list

    def process(self, data: dict) -> list:
        """
        输入：视频路径字典
        返回：多个字典列表，每个字典中包含一组 clip_seq
        clip_seq 是按相似度聚类后的 clip 路径序列
        """
        # 初始化 CLIP 模型和预处理器（只需加载一次）
        if not self.model:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            model = imagebind_model.imagebind_huge(pretrained=False)
            checkpoint_path = get_model_path("imagebind_huge.pth")
            state_dict = torch.load(checkpoint_path, map_location="cpu")
            model.load_state_dict(state_dict, strict=False)
            self.model = model.eval().to(self.device)

        model = self.model

        # 从 data 中取出相关路径信息
        video_path = data["path"]
        clip_dir_base = self.middel_result_save_dir
        frame_dir_base = self.middel_result_save_dir
        # 用视频路径生成唯一哈希，用于命名
        video_path_md5_hash = hashlib.md5(video_path.encode("utf-8")).hexdigest()

        # 按照视频内容切分成 clip 片段路径
        clip_paths = self.split_video_by_content(
            video_path, clip_dir_base, video_path_md5_hash
        )

        # 创建帧存放目录
        os.makedirs(frame_dir_base, exist_ok=True)

        # 提取每个 clip 中若干帧，然后拼接成一张图再保存
        frames = [
            self.extract_frames_uniformly(clip_path, num_frames=3)
            for clip_path in clip_paths
        ]
        frame_paths = self.save_horizontal_concat(
            frames, frame_dir_base, video_path, video_path_md5_hash
        )

        # 载入拼接后的帧图像
        images = [Image.open(p).convert("RGB") for p in frame_paths]

        inputs = {
            ModalityType.VISION: imagebind.data.load_and_transform_vision_data(
                frame_paths, self.device
            ),
        }

        with torch.no_grad():
            embeddings = self.model(inputs)[ModalityType.VISION]

        # 计算相邻 clip 的相似度
        similarities = self.calculate_similarity(embeddings)

        # 在第一个 clip 前添加相似度 0，方便对齐
        similarities.insert(0, 0)
        # print(similarities)

        temp = []
        samples = []
        # 遍历相似度与对应 clip
        for similarity, clip_path in zip(similarities, clip_paths):
            if similarity > self.threshold_upper:
                # 相似度过高，直接略过该 clip
                continue
            elif similarity > self.threshold_lower:
                # 相似度中等，添加到当前 temp 序列
                temp.append(clip_path)
                # 如果 temp 长度达到 10，截断成一组
                if len(temp) >= 10:
                    samples.append(temp)
                    temp = []
            else:
                # 相似度低，结束当前序列并重新开始新序列
                if temp:
                    samples.append(temp)
                temp = [clip_path]

        # 遍历结束，如果 temp 中还有 clip，也要添加
        if temp:
            samples.append(temp)

        # 把 video_path_md5_hash 加入 data
        data["video_path_md5_hash"] = video_path_md5_hash

        # 同一序列clip不能相距太远，根据距离，切割结果
        clip_seqs = []
        for sample in samples:
            sample = self.find_subsequences_with_conditions(sample)
            clip_seqs.extend(sample)

        # 最终结果：为每个 clip 序列构造一个新的字典
        result = []
        for seq_idx, clip_seq in enumerate(clip_seqs):
            new_data = copy.deepcopy(data)
            new_data["clip_seq"] = clip_seq
            new_data["seq_idx"] = seq_idx
            result.append(new_data)

        return result
