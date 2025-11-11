from data_engine.core.base import BaseFilter
from pydantic import Field
import os, av, re, random
from loguru import logger
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor

import copy
import re
import torch
import os
import random
from tqdm import tqdm
import json
from PIL import Image
import math, argparse
import io
import tempfile
from data_engine.utils.model_utils import get_model_path


class VideoMapperMainObjectDetection(BaseFilter):
    """
    主目标检测
    用于从给定视频中提取帧，整合成拼接图像，然后使用 Qwen 模型识别视频中最常见且一致出现的实体。
    重点功能：
    - 抽取视频帧
    - 拼接成网格图像
    - 使用大模型识别主要实体
    - 过滤掉无用片段
    - 判断人物一致性
    交错视频工作流专用算法
    交错视频所有的中间结果目录需要设置为相同的目录
    输出字段
    good_clips:视频抽取后单个新视频绝对路径#list[str]
    entity:识别出的实体名称#str
    good_clip_idx:有效片段的索引列表#list[int]
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(
        self,
        model_name_or_path: str,
        middel_result_save_dir: str = "middle_result",
        min_pixels: int = 200704,
        max_pixels: int = 1003520,
        **kwargs,
    ):
        """
        初始化方法
        model_name_or_path: 模型权重路径#模型权重路径
        middel_result_save_dir: 中间结果存储目录#中间结果存储目录
        min_pixels: 模型输入最小像素数#模型输入最小像素数
        max_pixels: 模型输入最大像素数#模型输入最小像素数
        """
        super().__init__(**kwargs)
        self.model = None
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.min_pixels = min_pixels
        self.max_pixels = max_pixels
        middel_result_save_dir = self.get_default_dir(middel_result_save_dir)
        self.middel_result_save_dir = middel_result_save_dir

    def save_image_temp(self, img: Image.Image, dir_path: str):
        """将 PIL 图像临时存储为 PNG 文件并返回文件路径"""
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 创建唯一的临时文件并返回路径
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".png", dir=dir_path
        ) as temp_file:
            temp_path = temp_file.name
            img.save(temp_path)  # 将图像保存到临时文件
            return temp_path

    def get_merged_img_auto(self, frames, batch_size=None):
        """
        拼接一批帧成网格图像
        根据输入帧数量自动确定网格大小，按需缩放
        """

        l = len(frames)

        images = [Image.open(frame).convert("RGB") for frame in frames]

        img_width, img_height = images[0].size

        # if l == 4 or l == 8:
        #     batch_size = 4
        # else:
        #     batch_size = 6
        if batch_size == None:
            batch_size = l

        merged_images = []
        for i in range(0, len(images), batch_size):
            # 获取当前批次的图像
            batch_images = images[i : i + batch_size]

            # 计算当前批次的行数和列数
            img_grid_w = max(math.ceil(math.sqrt(len(batch_images))), 1)
            img_grid_h = math.ceil(len(batch_images) / img_grid_w)

            if img_width > img_height:
                img_grid_w, img_grid_h = img_grid_h, img_grid_w

            # 创建一个空白画布
            grid_image = Image.new(
                "RGB", (img_grid_w * img_width, img_grid_h * img_height)
            )

            # 将图像粘贴到网格中
            for index, image in enumerate(batch_images):
                x = (index % img_grid_w) * img_width
                y = (index // img_grid_w) * img_height
                grid_image.paste(image, (x, y))

            # 计算目标尺寸
            target_height = img_grid_h * img_height
            target_width = img_grid_w * img_width

            # 判断是否需要缩放
            if target_height > 1200:
                scale_factor = 1200 / target_height
                target_width = int(target_width * scale_factor)
                target_height = int(target_height * scale_factor)

            grid_image = grid_image.resize(
                (target_width, target_height), Image.Resampling.LANCZOS
            )

            # 将当前的合并图像添加到结果列表中
            merged_images.append(grid_image)
        return merged_images[0]

    def extract_frames_uniformly(self, video_path, num_frames=3):
        """
        均匀采样视频中 num_frames 帧
        Args:
            video_path (str): 视频路径
            num_frames (int): 要采样帧数
        Returns:
            frames (List[PIL.Image.Image]), clip_idx (int)
        """

        clip_idx = int(video_path.split("Scene-")[1].split(".")[0])

        container = av.open(video_path)
        stream = container.streams.video[0]

        duration_seconds = float(stream.duration * stream.time_base)
        avg_fps = float(stream.average_rate) if stream.average_rate else 0
        estimated_frames = int(duration_seconds * avg_fps)

        if estimated_frames <= 0:
            print(f"Warning: cannot estimate frames for {video_path}, skipping.")
            return []

        # 每段取中间位置的帧索引
        split_size = estimated_frames / (num_frames + 1)
        indices = [int(split_size * (i + 1)) for i in range(num_frames)]

        frames = []
        for i, frame in enumerate(container.decode(stream)):
            if i in indices:
                img = frame.to_image()
                frames.append(img)
            if i > max(indices):
                break

        return (frames, clip_idx)

    def save_vertical_concat(self, imgs_list, sample_save_dir, pad=0):
        """
        纵向拼接每组图像，图像间隔 pad 像素，并保存为图片。

        Args:
            imgs_list: List[List[PIL.Image], clip_idx]
            save_dir: 保存目录
            pad: 每张图之间的 padding，单位像素

        Returns:
            frame_paths: List[str] 保存的图片路径列表
        """
        save_dir = sample_save_dir
        os.makedirs(save_dir, exist_ok=True)
        frame_paths = []

        for imgs, clip_idx in imgs_list:
            widths, heights = zip(*(img.size for img in imgs))
            max_width = max(widths)
            total_height = sum(heights) + pad * (len(imgs) - 1)

            new_img = Image.new("RGB", (max_width, total_height), color=(255, 255, 255))
            y_offset = 0
            for img in imgs:
                new_img.paste(img, (0, y_offset))
                y_offset += img.size[1] + pad

            save_path = os.path.join(save_dir, f"video_frames_{clip_idx:05d}.jpg")
            new_img.save(save_path)
            frame_paths.append(save_path)

        return frame_paths

    def save_frames(self, frames, save_dir, prefix="frame"):
        """
        将已有的 PIL.Image 列表保存到指定目录，并返回保存路径列表。

        Args:
            frames (List[Image.Image]): 要保存的图像对象列表
            save_dir (str): 保存目录
            prefix (str): 文件名前缀（默认是 "frame"）

        Returns:
            List[str]: 保存的文件路径列表
        """
        os.makedirs(save_dir, exist_ok=True)
        saved_paths = []

        for i, img in enumerate(frames):
            save_path = os.path.join(save_dir, f"{prefix}_{i:05d}.jpg")
            img.save(save_path)
            saved_paths.append(save_path)

        return saved_paths

    def get_merged_img_pad(
        self, frames, img_grid_h=1, padding=10, padding_color=(255, 255, 255)
    ):
        print("frames,", frames)
        merged_rows = []
        for frame_list in frames:
            # 加载这一行所有图片
            images = [Image.open(p).convert("RGB") for p in frame_list]

            img_width, img_height = images[0].size
            batch_images = images
            img_grid_h = img_grid_h
            img_grid_w = math.ceil(len(batch_images) / img_grid_h)

            grid_image = Image.new(
                "RGB",
                (
                    img_grid_w * img_width + (img_grid_w - 1) * padding,
                    img_grid_h * img_height + (img_grid_h - 1) * padding,
                ),
                padding_color,
            )

            for index, image in enumerate(batch_images):
                x = (index % img_grid_w) * (img_width + padding)
                y = (index // img_grid_w) * (img_height + padding)
                grid_image.paste(image, (x, y))

            # 限制尺寸
            target_height = grid_image.height
            target_width = grid_image.width

            if target_height > 8000:
                scale_factor = 8000 / target_height
                target_width = int(target_width * scale_factor)
                target_height = int(target_height * scale_factor)

            if target_width > 60000:
                scale_factor = 60000 / target_width
                target_width = int(target_width * scale_factor)
                target_height = int(target_height * scale_factor)

            grid_image = grid_image.resize(
                (target_width, target_height), Image.Resampling.LANCZOS
            )
            merged_rows.append(grid_image)

        # 拼接所有行
        total_height = sum(img.height for img in merged_rows) + padding * (
            len(merged_rows) - 1
        )
        max_width = max(img.width for img in merged_rows)
        final_image = Image.new("RGB", (max_width, total_height), padding_color)

        current_y = 0
        for img in merged_rows:
            final_image.paste(img, (0, current_y))
            current_y += img.height + padding

        return final_image

    def cal_qwen(self, messages, model, processor):
        # Preparation for inference
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return output_text[0]

    def cal_qwen_entity(self, img, l, model, processor):

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": img,
                    },
                    {
                        "type": "text",
                        "text": f"""
                                There {l} pictures. Each column is a picture. 
                                Can you identify the most common entities (objects/people/goals) among these images? 
                                Note:
                                1) Only return the most common entity, such as one person or one object.
                                2) The entity must be the same one.
                                3) The one must be the main entity, not the background or edge entity.
                                4) The entity must appear in more than 60% of the images. Return 'none' if there are none."
                                5) Return the entity name directly, with its characteristics. 
                                6）The same person is also an entity, return person‘s characteristics(hair, dress), don't guess person‘s name.
                                """,
                    },
                ],
            }
        ]
        return self.cal_qwen(messages, model, processor)

    def cal_qwen_ifexist_entity(self, img_path, object, model, processor):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": img_path,
                    },
                    {
                        "type": "text",
                        "text": f"""
                                Is there "{object}" in the picture?
                                """,
                    },
                ],
            }
        ]
        return self.cal_qwen(messages, model, processor)

    def cal_qwen_ifone(self, img_path, object, model, processor):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": img_path,
                    },
                    {
                        "type": "text",
                        "text": f"""
                                Is there more than one "{object}" in the picture?
                                """,
                    },
                ],
            }
        ]

        return self.cal_qwen(messages, model, processor)

    def cal_qwen_ispeople(self, object, model, processor):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                                Is "{object}" refers to people?
                                """,
                    },
                ],
            }
        ]

        return self.cal_qwen(messages, model, processor)

    def cal_qwen_same_person(self, img_path, object, l, model, processor):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": img_path,
                    },
                    {
                        "type": "text",
                        "text": f"""
                                There are {l} pictures here. Are the "{object}" in each picture the same person?
                                """,
                    },
                ],
            }
        ]

        return self.cal_qwen(messages, model, processor)

    def find_subsequences_with_conditions(self, lst, max_gap=5, min_length=2):
        subsequences = []  # 用来存储符合条件的子串的列表

        if len(lst) == 0:
            return []

        # 变量初始化
        current_subseq = [lst[0]]  # 初始子串包含第一个元素

        for i in range(1, len(lst)):
            # 判断当前数字与前一个数字的差是否在允许的最大间隔内
            current_value = int(lst[i][0].split("/")[-1].split("_")[0])
            prev_value = int(lst[i - 1][0].split("/")[-1].split("_")[0])
            # print(lst, current_value)
            # 判断当前数字与前一个数字的差是否在最大间隔范围内
            if current_value - prev_value <= max_gap:
                # 如果当前子串的长度小于 10，添加当前元素
                if len(current_subseq) < 10:
                    current_subseq.append(lst[i])  # 如果符合条件，则加入当前子串
                else:
                    # 如果当前子串已满，添加到结果列表，并开始新的子串
                    subsequences.append(current_subseq)
                    current_subseq = [lst[i]]  # 重新开始新的子串
            else:
                # 如果当前子串的长度大于最小长度，则添加到结果
                if len(current_subseq) >= min_length:
                    subsequences.append(current_subseq)
                current_subseq = [lst[i]]  # 重新开始新的子串

        # 最后检查一次当前子串，确保它被添加到结果中
        if len(current_subseq) >= min_length:
            subsequences.append(current_subseq)

        return subsequences

    def create_replacer(self, replacements):
        def replacer(match):
            return replacements.pop(0)

        return replacer

    def get_model(self):
        if not self.model:
            # model = Qwen2VLForConditionalGeneration.from_pretrained(
            #     self.model_name_or_path, torch_dtype="auto", device_map="auto").eval()

            model = (
                Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_name_or_path, torch_dtype=torch.float16
                )
                .to("cuda")
                .eval()
            )
            processor = AutoProcessor.from_pretrained(
                self.model_name_or_path,
                min_pixels=self.min_pixels,
                max_pixels=self.max_pixels,
            )
            self.model = model, processor
        return

    def process(self, data: dict):
        """
        处理单个视频片段序列
        包括：
        - 抽帧
        - 拼接
        - 模型识别实体
        - 判断一致性与人物过滤
        返回更新后的 data 或 None
        """
        self.get_model()

        model, processor = self.model

        video_path = data["path"]
        clip_dir_base = self.middel_result_save_dir
        frame_dir_base = self.middel_result_save_dir
        video_path_md5_hash = data["video_path_md5_hash"]
        clip_seq = data["clip_seq"]
        seq_idx = data["seq_idx"]

        sample_save_dir = os.path.join(
            self.middel_result_save_dir, video_path_md5_hash, f"{seq_idx:05d}"
        )

        frame_seqs = [
            self.extract_frames_uniformly(video_path) for video_path in clip_seq
        ]
        merged_frame_paths = self.save_vertical_concat(frame_seqs, sample_save_dir)

        frame2video_dict = {}
        for merged_frame_path, video_path in zip(merged_frame_paths, clip_seq):
            frame2video_dict[merged_frame_path] = video_path

        split_frame_paths = [
            self.save_frames(
                frame_seq,
                os.path.join(sample_save_dir, f"video_{clip_idx:05d}"),
                "split",
            )
            for frame_seq, clip_idx in frame_seqs
        ]
        middle_frame_paths = [
            self.save_frames(
                [frame_seq[1]],
                os.path.join(sample_save_dir, f"video_{clip_idx:05d}"),
                "middle",
            )
            for frame_seq, clip_idx in frame_seqs
        ]

        responses = []

        sample_merged_middle = self.get_merged_img_pad(middle_frame_paths)
        sample_merged_middle.save(
            os.path.join(sample_save_dir, "sample_merged_middle.jpg")
        )

        sample_merged_split = self.get_merged_img_pad(split_frame_paths)
        sample_merged_split.save(
            os.path.join(sample_save_dir, "sample_merged_split.jpg")
        )

        # 获得主要entity
        response_search_entity = self.cal_qwen_entity(
            sample_merged_middle, len(middle_frame_paths), model, processor
        )

        responses.append(f"response_search_entity:  {response_search_entity}")
        if "none" in response_search_entity or "None" in response_search_entity:
            return {}

        entity = response_search_entity.split("is", 1)[-1]
        entity_ispeople = False

        # 检查entity是否指的是人
        response_ispeople = self.cal_qwen_ispeople(entity, model, processor)
        responses.append(f"response_ispeople:  {response_ispeople}")
        if "Yes" in response_ispeople:
            entity_ispeople = True

        good_clips = []
        for i, frame3_path in enumerate(merged_frame_paths):
            # 处理单个切片
            frame3_split_path = split_frame_paths[i]

            per_frame_paths = frame3_split_path

            # 检查是否有entity
            ifexist_entiy = False
            # 处理切片的三个frame
            for frame_id, per_frame_path in enumerate(
                per_frame_paths
            ):  # frame_id : 0, 1, 2
                response_ifexist_entiy = self.cal_qwen_ifexist_entity(
                    per_frame_path, entity, model, processor
                )
                responses.append(f"response_ifexist_entiy:  {response_ifexist_entiy}")
                if "Yes" in response_ifexist_entiy:
                    ifexist_entiy = True
                    good_idx = frame_id
                    good_img = per_frame_path
                    break

            if ifexist_entiy:
                good_clips.append((frame3_path, good_img))

        # 如果是人,检查是否是一个人,并过滤掉多个人的图片
        if entity_ispeople:
            response_ifones = []
            for good_clip in good_clips:
                response_ifone = self.cal_qwen_ifone(
                    good_clip[1], entity, model, processor
                )
                responses.append(f"response_ifone:  {str(response_ifone)}")
                response_ifones.append(response_ifone)

            temp_good_clips = []
            for response_ifone, good_clip in zip(response_ifones, good_clips):
                if "Yes" in response_ifone:
                    continue
                else:
                    temp_good_clips.append(good_clip)
            good_clips = temp_good_clips

        if len(good_clips) < 2:
            return {}

        if entity_ispeople:
            # 判断是不是同一个人
            merged_img = self.get_merged_img_auto([x[1] for x in good_clips])
            response_same_person = self.cal_qwen_same_person(
                merged_img, entity, len(good_clips), model, processor
            )
            responses.append(("response_same_person:  ", response_same_person))
            if not ("Yes" in response_same_person):
                return {}

        good_clips = [frame2video_dict[x[0]] for x in good_clips]
        data["good_clips"] = good_clips

        good_clip_idx = [
            int(os.path.basename(c).split("-")[-1].split(".")[0]) for c in good_clips
        ]

        data["good_clips"] = good_clips
        data["entity"] = entity
        data["good_clip_idx"] = good_clip_idx

        return data
