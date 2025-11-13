#!/usr/bin/env python3
# video_aesthetics_filter.py

import os
import shutil
import torch
from loguru import logger
import cv2
import numpy as np
from PIL import Image
from aesthetics_predictor import AestheticsPredictorV2Linear
from data_engine.core.base import BaseFilter
from transformers import CLIPProcessor
from data_engine.utils.model_utils import get_model_path


def extract_uniform_frames(video_path: str, num_frames: int):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        raise RuntimeError(f"No frames found in video: {video_path}")
    ids = np.linspace(0, total - 1, num_frames, dtype=int)
    frames = []
    for fid in ids:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        ret, frame = cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb))
    cap.release()
    return frames


def score_video(video_path: str, model, processor, num_frames: int, reduce_mode: str, normalize: bool):
    frames = extract_uniform_frames(video_path, num_frames)
    scores = []
    for img in frames:
        inputs = processor(images=img, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output = model(**inputs)
        if hasattr(output, "logits"):
            score = output.logits.squeeze().item()
        elif isinstance(output, torch.Tensor):
            score = output.item()
        else:
            raise TypeError(f"Unexpected model output type: {type(output)}")

        if normalize:
            score /= 10.0
        scores.append(score)

    scores = np.array(scores, dtype=float)
    if reduce_mode == "avg":
        return float(scores.mean())
    elif reduce_mode == "max":
        return float(scores.max())
    elif reduce_mode == "min":
        return float(scores.min())
    else:
        raise ValueError(f"Unsupported reduce_mode: {reduce_mode}")



class VideoFilterAesthetics(BaseFilter):
    """
    美学评分过滤器：
    对视频进行抽帧并计算平均/最大/最小美学得分，
    若开启过滤，则筛除分数不在区间 [min_score, max_score] 内的视频。
    """
    use_class = True

    def __init__(
        self,
        model_name: str = "aesthetics-predictor-v2-sac-logos-ava1-l14-linearMSE",
        min_score: float = 0.4,
        max_score: float = 1.0,
        num_frames: int = 3,
        reduce_mode: str = "avg",
        do_filter: bool = False,
        **kwargs,
    ):
        super().__init__(do_filter=do_filter, **kwargs)
        self.model_name = get_model_path(model_name)
        self.min_score = min_score
        self.max_score = max_score
        self.num_frames = num_frames
        self.reduce_mode = reduce_mode
        self.normalize = "v2" in self.model_name.lower()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None

    def process(self, row: dict) -> dict:
        video_path = row["path"]

        # 延迟加载模型与processor
        if self.model is None:
            logger.info(f"Loading aesthetics model from {self.model_name}")
            self.model = AestheticsPredictorV2Linear.from_pretrained(self.model_name).to(self.device)
            clip_name = get_model_path("clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained(clip_name)

        score = score_video(
            video_path,
            self.model,
            self.processor,
            self.num_frames,
            self.reduce_mode,
            self.normalize,
        )
        row["aesthetics_score"] = score

        if self.do_filter and not (self.min_score <= score <= self.max_score):
            logger.debug(f"Filtered out {video_path} with score {score:.3f}")
            return {}
        return row
