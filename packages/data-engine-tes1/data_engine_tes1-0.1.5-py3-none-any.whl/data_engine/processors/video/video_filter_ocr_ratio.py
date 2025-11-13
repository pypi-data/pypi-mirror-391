from data_engine.core.base import BaseFilter
from typing import Optional
import hashlib, s3fs
from PIL import Image
from decord import VideoReader
import cv2, os, time
import numpy as np
from loguru import logger
from paddleocr import PaddleOCR
import resource
import psutil, os, gc
from data_engine.utils.model_utils import get_model_path


class VideoFilterOcrRatio(BaseFilter):
    """
    文字占比
    使用PaddleOCR模型对采样帧中的文本区域进行检测与识别，返回文本边界框及占比面积，用于文本出现频率和大小分析。
    输出字段
    path: 输入的视频路径#str
    resolution: 视频分辨率，格式为 [高度，宽度，通道数] #list[int,int,int]
    text_boxes: 所有采样帧中检测到的文本边界框信息#list[float,float,float]
    text_areas: 所有采样帧中检测到的文本区域占比#list[float,float,float]
    avg_ocr_area: 所有采样帧的平均文本区域占比 #float
    ocr_time: OCR 处理的总耗时（秒）#float
    max_memory: 处理过程中使用的最大内存 #int(KB)
    """

    use_class = True

    def __init__(
        self,
        det_model_dir: str = "ch_PP-OCRv3_det_infer",
        rec_model_dir: str = "ch_PP-OCRv3_rec_infer",
        cls_model_dir: str = "ch_ppocr_mobile_v2.0_cls_infer",
        **kwargs,
    ):
        """
        初始化方法
        det_model_dir: 检测模型#检测模型
        rec_model_dir: 识别模型#识别模型
        cls_model_dir: 方向分类模型#方向分类模型
        """
        self.det_model_dir = get_model_path(det_model_dir)
        self.rec_model_dir = get_model_path(rec_model_dir)
        self.cls_model_dir = get_model_path(cls_model_dir)
        self.ocr_model = None
        super().__init__(**kwargs)

    def get_model(self):
        if self.ocr_model is None:
            self.ocr_model = PaddleOCR(
                det_model_dir=self.det_model_dir,
                rec_model_dir=self.rec_model_dir,
                cls_model_dir=self.cls_model_dir,
                use_angle_cls=True,
                show_log=False,
            )

    def get_frames(self, video_path):
        def compute_all_indices(video_fps, start_frame, end_frame):
            total_duration = (end_frame - start_frame) / video_fps

            # === 抽帧（每2秒1帧，最多20帧） ===
            ocr_interval = int(video_fps * 2)
            ocr_ids = np.arange(start_frame, end_frame, ocr_interval).astype(int)
            if len(ocr_ids) > 20:
                ocr_ids = ocr_ids[:20]
            return ocr_ids

        try:
            vr = VideoReader(video_path)
            video_fps = vr.get_avg_fps()
            total_frames = len(vr)
            start_frame = 0
            end_frame = total_frames

            ocr_ids = compute_all_indices(video_fps, start_frame, end_frame)
            frames_all = vr.get_batch(ocr_ids).asnumpy()
            frame = vr[0]  # 获取第一帧
            height, width, _ = frame.shape

        except Exception as e:
            logger.exception(
                "[WARN] Decord failed for, fallback to OpenCV. Error: {}", e
            )
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError("Cannot open video")

            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            start_frame = 0
            end_frame = total_frames

            ocr_ids = compute_all_indices(video_fps, start_frame, end_frame)

            frames = []
            for idx in ocr_ids:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            if not frames or len(frames) != len(ocr_ids):
                raise RuntimeError("OpenCV could not extract all frames")
            frames_all = np.stack(frames)

        return frames_all, width, height

    def get_text_bboxes(self, frames, ocr_model):
        """获取文本边界框"""
        bboxes, areas = [], []
        cal_area = lambda bb: abs(bb[1][0] - bb[0][0]) * abs(bb[2][1] - bb[1][1])

        for frame in frames:
            h, w = frame.shape[:2]
            try:
                result = ocr_model.ocr(frame, cls=True)
                bbox = [line[0] for line in result[0]] if result and result[0] else []
                bboxes.append(bbox)
                areas.append([cal_area(bb) / h / w for bb in bbox] if bbox else [0])
            except:
                bboxes.append([])
                areas.append([0])

        return bboxes, areas

    def _process(self, scene_info):
        self.get_model()
        s = time.time()
        frames, width, height = self.get_frames(scene_info["path"])
        scene_info["resolution"] = [height, width, 3]

        scene_info["text_boxes"], scene_info["text_areas"] = self.get_text_bboxes(
            frames, self.ocr_model
        )
        del frames
        gc.collect()

        scene_info["avg_ocr_area"] = (
            np.mean([sum(a) for a in scene_info["text_areas"]])
            if scene_info["text_areas"]
            else 0
        )
        scene_info["ocr_time"] = time.time() - s
        scene_info["max_memory"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if scene_info["text_boxes"] is not None:
            scene_info["text_boxes"] = str(scene_info["text_boxes"])
        if scene_info["text_areas"] is not None:
            scene_info["text_areas"] = str(scene_info["text_areas"])
        return scene_info

    def process(self, scene_info) -> dict:
        try:
            scene_info = self._process(scene_info)
            return scene_info
        except Exception as e:
            # if os.path.exists(scene_info.get("path", "")):
            #     os.remove(scene_info["path"])
            raise e
