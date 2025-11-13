import cv2
import numpy as np


def extract_frames(video_source, num_frames=None, frame_interval=None):
    """
    从视频中抽取帧，支持两种模式：
      1. 均匀抽取指定数量的帧（num_frames 模式）
      2. 按固定间隔抽取帧（frame_interval 模式）

    参数:
        video_source (str or cv2.VideoCapture): 视频文件路径或已打开的 cv2.VideoCapture 对象
        num_frames (int, optional): 期望抽取的帧数，需大于1
        frame_interval (int, optional): 两帧之间的间隔（步长），需大于0

    返回:
        frames (list of ndarray): 抽取的帧列表
        actual_count (int): 实际抽取的帧数

    说明:
        - 两种模式互斥，优先使用 frame_interval。如果两者都未指定或参数非法，将抛出 ValueError。
        - 若 num_frames 模式下请求的帧数超过视频实际帧数，则返回所有帧。
    """
    # 校验模式
    if frame_interval is not None:
        if not isinstance(frame_interval, int) or frame_interval <= 0:
            raise ValueError("frame_interval must be an integer greater than 0")
        mode = "interval"
    elif num_frames is not None:
        if not isinstance(num_frames, int) or num_frames <= 1:
            raise ValueError("num_frames must be an integer greater than 1")
        mode = "uniform"
    else:
        raise ValueError("Either num_frames or frame_interval must be provided")

    # 打开视频
    owns_capture = False
    if isinstance(video_source, str):
        cap = cv2.VideoCapture(video_source)
        owns_capture = True
    elif isinstance(video_source, cv2.VideoCapture):
        cap = video_source
    else:
        raise TypeError("video_source must be a file path or cv2.VideoCapture instance")

    # 获取总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        # 回退到手动读取以获取帧数
        total_frames = 0
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            total_frames += 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # 生成帧索引
    if mode == "interval":
        indices = list(range(0, total_frames, frame_interval))
        actual_count = len(indices)
        if actual_count == 0:
            return [], 0
    else:  # uniform
        actual_count = min(total_frames, num_frames)
        indices = np.linspace(0, total_frames - 1, actual_count, dtype=int)

    # 执行抽取
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    if owns_capture:
        cap.release()

    return frames, len(frames)
