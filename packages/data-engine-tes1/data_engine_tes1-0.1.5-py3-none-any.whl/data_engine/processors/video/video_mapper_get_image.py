from data_engine.core.base import BaseFilter
from typing import Optional
import hashlib, s3fs
from PIL import Image
from decord import VideoReader
import cv2, os, time
import numpy as np
import resource
import psutil, os, gc


class VideoMapperGetImage(BaseFilter):
    """
    从视频中抽取帧合并成单张图片
    自适应的从视频中均匀抽取帧合并成单张图片，视频时长小于5秒抽取2帧，小于10秒抽取6帧，否则抽取9帧
    输出字段
    image_path: 合成图片的保存路径，默认是image_path #str

    """

    def __init__(
        self,
        image_root: str = None,
        unique_column: str = "video_id",
        result_col: str = "image_path",
        **kwargs,
    ):
        """
        初始化方法
        image_root: 保存图片的路径#保存图片的路径
        unique_column: 视频唯一id值#视频唯一id值
        result_col: 结果存储的字段名称#结果存储的字段名称
        """
        super().__init__(**kwargs)
        self.image_root = self.get_default_dir(image_root)
        self.unique_column = unique_column
        self.result_col = result_col

    def uniform_sample_indices(self, start_frame, end_frame, num_samples):
        if num_samples <= 0 or end_frame <= start_frame:
            return np.array([], dtype=int)
        return np.linspace(start_frame, end_frame - 1, num_samples).astype(int)

    def get_frames(self, video_path):
        def compute_all_indices(video_fps, start_frame, end_frame):
            total_duration = (end_frame - start_frame) / video_fps
            merge_count = 3 if total_duration <= 5 else 6 if total_duration <= 10 else 9
            merge_ids = self.uniform_sample_indices(start_frame, end_frame, merge_count)

            return merge_ids

        try:
            vr = VideoReader(video_path)
            video_fps = vr.get_avg_fps()
            total_frames = len(vr)
            start_frame = 0
            end_frame = total_frames

            merge_ids = compute_all_indices(video_fps, start_frame, end_frame)
            frames_all = vr.get_batch(merge_ids).asnumpy()

        except Exception as e:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"[ERROR] Cannot open video: {video_path}")
                return None

            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            start_frame = 0
            end_frame = total_frames

            merge_ids = compute_all_indices(video_fps, start_frame, end_frame)

            frames = []
            for idx in merge_ids:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            cap.release()

            if not frames:
                raise RuntimeError("[ERROR] OpenCV could not extract all frames.")
            frames_all = np.stack(frames)

        return frames_all

    def merge_images_to_jpg(self, frames, video_id):
        image_filename = f"{video_id}.jpg"
        # os.makedirs(os.path.join(self.image_root, video_id), exist_ok=True)
        output_path = os.path.join(self.image_root, image_filename)
        """
        根据提供的图像列表（如3张图像为一行，6张图像为两行），
        动态合并图像并保存为一个 JPG 文件。

        :param frames: 需要合并的帧列表（包含图像）
        :param output_path: 合并后的图像保存路径
        """
        # 每行最多显示 3 张图像
        images_per_row = 3
        num_images = len(frames)

        # 将 numpy 数组转换为 Image 对象
        images = [Image.fromarray(frame) for frame in frames]

        # 计算每张图像的宽度和高度
        widths, heights = zip(*(i.size for i in images))

        # 计算每行的宽度和总高度
        rows = (num_images + images_per_row - 1) // images_per_row  # 计算总行数
        total_width = images_per_row * max(
            widths
        )  # 总宽度为 3 张图像的宽度之和（每列最大宽度）
        total_height = sum(heights[i] for i in range(rows))  # 总高度为每行的高度之和

        # 创建一个新的图像，宽度为所有图片宽度之和，高度为总高度
        new_image = Image.new(
            "RGB", (total_width, total_height), (255, 255, 255)
        )  # 设置白色背景

        # 将每张图片粘贴到合适的位置
        x_offset = 0
        y_offset = 0
        row_height = 0  # 每一行的高度
        for i, img in enumerate(images):
            # 每 3 张图像换行
            if i > 0 and i % images_per_row == 0:
                x_offset = 0
                y_offset += row_height  # 更新 y 坐标，换行
                row_height = 0  # 重置当前行的高度

            # 更新每行的最大高度
            row_height = max(row_height, img.height)

            # 粘贴图像
            new_image.paste(img, (x_offset, y_offset))
            x_offset += img.width  # 更新 x 坐标

        # 保存合并后的图像为 JPG 文件
        with open(output_path, "wb") as f:
            new_image.save(f, format="JPEG")
        return output_path

    def _process(self, scene_info):
        frames = self.get_frames(scene_info["path"])

        # === 合成图像 ===
        scene_info[self.result_col] = self.merge_images_to_jpg(
            frames, str(scene_info[self.unique_column])
        )
        return scene_info

    def process(self, scene_info) -> dict:
        cv2.setNumThreads(5)
        scene_info = self._process(scene_info)
        return scene_info
