from data_engine.core.base import BaseFilter
from typing import Optional
from decord import VideoReader
import cv2, os, time
import numpy as np
from loguru import logger
import resource
import psutil, os, gc


class VideoFilterMotionScore(BaseFilter):
    """
    视频运动分计算
    通过光流计算视频片段的运动强度
    """

    def __init__(
        self,
        min_value: int = 5,
        **kwargs,
    ):
        """
        初始化方法。
        min_value: 最小的运动分数 # 最小的运动分数
        """
        self.min_value = min_value
        super().__init__(**kwargs)

    def get_frames(self, video_path):
        def compute_all_indices(video_fps, start_frame, end_frame):
            total_duration = (end_frame - start_frame) / video_fps

            # === 1. 前30秒 motion 抽帧 ===
            max_30s_frame = start_frame + int(min(total_duration, 30) * video_fps)
            frame_step = int(video_fps / 2)  # 1秒2帧
            if total_duration >= 30:
                motion_ids = np.arange(start_frame, max_30s_frame, frame_step).astype(
                    int
                )
            else:
                motion_ids = np.arange(start_frame, end_frame, frame_step).astype(int)
            return motion_ids

        try:
            vr = VideoReader(video_path)
            video_fps = vr.get_avg_fps()
            total_frames = len(vr)
            start_frame = 0
            end_frame = total_frames

            motion_ids = compute_all_indices(video_fps, start_frame, end_frame)
            frames_all = vr.get_batch(motion_ids).asnumpy()
            frame = vr[0]  # 获取第一帧

        except Exception as e:
            print(
                f"[WARN] Decord failed for {video_path}, fallback to OpenCV. Error: {e}"
            )
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"[ERROR] Cannot open video")

            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            start_frame = 0
            end_frame = total_frames

            motion_ids = compute_all_indices(video_fps, start_frame, end_frame)

            frames = []
            for idx in motion_ids:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            cap.release()

            if not frames or len(frames) != len(motion_ids):
                raise RuntimeError("OpenCV could not extract all frames.")
            frames_all = np.stack(frames)

        return frames_all

    def calculate_optical_flow(self, frames):
        """计算光流"""
        flow_list = []
        for idx in range(len(frames) - 1):
            gray_pre = cv2.cvtColor(frames[idx], cv2.COLOR_RGB2GRAY)
            gray_next = cv2.cvtColor(frames[idx + 1], cv2.COLOR_RGB2GRAY)

            p0 = cv2.goodFeaturesToTrack(
                gray_pre,
                mask=None,
                maxCorners=100,
                qualityLevel=0.1,
                blockSize=7,
                minDistance=7,
            )
            if p0 is None or len(p0) == 0:
                flow_list.append(0)
                continue

            p1, st, _ = cv2.calcOpticalFlowPyrLK(
                gray_pre, gray_next, p0, None, winSize=(15, 15), maxLevel=2
            )
            good_new = p1[st == 1]
            good_old = p0[st == 1]
            dists = [
                abs(a - c) + abs(b - d)
                for (a, b), (c, d) in zip(
                    good_new.reshape(-1, 2), good_old.reshape(-1, 2)
                )
                if abs(a - c) + abs(b - d) > 2
            ]
            flow_list.append(sum(dists) / len(dists) if dists else 0)

        return flow_list

    def _process(self, scene_info):
        start = time.time()
        frames = self.get_frames(scene_info["path"])
        # === optical flow ===
        scene_info["optical_flow"] = self.calculate_optical_flow(frames)
        scene_info["avg_optical_flow"] = (
            sum(scene_info["optical_flow"]) / len(scene_info["optical_flow"])
            if scene_info["optical_flow"]
            else 0
        )
        if scene_info["avg_optical_flow"] < self.min_value:
            if os.path.exists(scene_info.get("path", "")):
                os.remove(scene_info["path"])
            return {}

        del frames
        gc.collect()
        take_time = time.time() - start
        scene_info["motion_time"] = take_time
        if scene_info["optical_flow"] is not None:
            scene_info["optical_flow"] = [
                np.float32(i) for i in scene_info["optical_flow"]
            ]
        return scene_info

    def process(self, scene_info) -> dict:
        cv2.setNumThreads(5)
        try:
            scene_info = self._process(scene_info)
            return scene_info
        except Exception as e:
            if os.path.exists(scene_info.get("path", "")):
                os.remove(scene_info["path"])
            raise e
