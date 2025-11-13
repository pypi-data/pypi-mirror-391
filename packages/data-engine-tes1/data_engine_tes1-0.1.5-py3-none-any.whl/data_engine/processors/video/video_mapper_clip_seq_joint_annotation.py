import json
import time, torch
from PIL import Image
import os
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
import re, math
from data_engine.utils.model_utils import get_model_path
from data_engine.core.base import BaseFilter


class VideoMapperClipSeqJointAnnotation(BaseFilter):
    """
    基于视频切片的联合描述生成
    用途：描述两个连续 clip 之间的延续与变化，包括：
    - 内容延续与变化
    - 环境延续与变化
    - 相机角度与移动变化
    并用模型生成描述
    交错视频工作流专用算法
    交错视频所有的中间结果目录需要设置为相同的目录
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(
        self,
        model_name_or_path: str,
        min_pixels: int = 200704,
        max_pixels: int = 1003520,
        middel_result_save_dir: str = "middle_result",
        **kwargs,
    ):
        """
        初始化方法
        model_name_or_path: 模型权重路径#模型权重路径
        middel_result_save_dir: 中间结果文件夹路径#中间结果文件夹路径
        min_pixels: 模型输入最小像素限制#模型输入最小像素限制
        max_pixels: 模型输入最大像素限制#模型输入最大像素限制
        """
        super().__init__(**kwargs)
        self.model = None
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.min_pixels = min_pixels
        self.max_pixels = max_pixels
        middel_result_save_dir = self.get_default_dir(middel_result_save_dir)
        self.middel_result_save_dir = middel_result_save_dir

    def cal_response_diff(self, response_singles, diff_paths):
        """
        对一对 clip 序列生成比较描述
        Args:
            response_singles (List[str]): 单个 clip 的描述结果
            diff_paths (List[str]): 两个 clip 拼接后的对照图路径
        Returns:
            response_texts (List[str]): 模型生成的描述结果
        """
        response_texts = []
        for i, diff_path in enumerate(diff_paths[:]):
            content = []
            h_response_single = response_singles[i]
            t_response_single = response_singles[i + 1]

            prompt_single = {
                "type": "text",
                "text": f"""    
                                Here are two consecutive video clips along with their descriptions:
                                # the first clip description: {h_response_single}
                                # the second clip description: {t_response_single}
                                The second clip continues the theme of the first clip. Based on the provided frames, please describe the continuation and differences between the two clips in terms of:
                                1) the continuation part and change in video content (characters, objects,key, actions, the unfolding plot, and visual details, about 300 words)       
                                2) the continuation part and change in background (the environmental factors, lighting, space, surrounding elements that provide context to the scene, about 60 words）
                                3) the change in camera angle (the perspective from which the camera captures the main object or scene, about 30 words)
                                4) the change in camera movement (panning, tilting, and tracking, as well as changes in zoom (in or out) and focus, about 30 words）                           
                                Do not analyze, subjective interpretations, aesthetic rhetoric, such as "context", "atmosphere", "suggest", "drama", etc. focus solely on objective descriptions.
                                DO not including any reasoning description like "suggest", "indicate", "probably because", "appears to be".
                                **Directly return in the json format like this:
                                {{"continuation_in_video_content": "...", "change_in_video_content": "...", "continuation_in_video_background": "...", "change_in_video_background": "...", "change_in_camera_angle": "...", "change_in_camera_movement": "...",   }}.  
                                #[clip frames of the first clip (above row) and the second clip (bottom row)]:
                        """,
            }

            content.append(prompt_single)
            content = self.add_img([diff_path], content)

            messages = [{"role": "user", "content": content}]

            retries = 0
            max_retries = 20
            retry_delay = 10

            while retries < max_retries:
                try:
                    response_text = self.cal_qwen(messages)
                    response_texts.append(response_text)
                    break  # 成功获取响应后跳出重试循环
                except Exception as e:  # 捕获异常
                    print(f"请求失败，重试 {retries + 1}/{max_retries} 次，错误: {e}")
                    retries += 1
                    if retries >= max_retries:
                        raise Exception(
                            "超过最大重试次数，无法获取响应"
                        )  # 超过最大重试次数抛出异常
                    time.sleep(retry_delay)  # 暂停后继续重试

            # 如果在超过最大重试次数后仍未成功，将抛出异常
            if retries >= max_retries:
                raise Exception("请求失败，超过最大重试次数")

        return response_texts

    def add_img(self, imgs, content, text=""):
        # imgs = [code_img(img) for img in imgs]

        for i, img in enumerate(imgs):
            content.append(
                {
                    "type": "image",
                    "image": img,
                }
            )
        return content

    def get_merged_img_pad(
        self, frames, img_grid_h=1, padding=10, padding_color=(255, 255, 255)
    ):
        """
        拼接一对 clip 对照图
        Args:
            frames: 二维列表，如 [[clip1_frame1,...], [clip2_frame1,...]]
        Returns:
            PIL.Image 拼接后的图像
        """
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

    def cal_qwen(self, messages):
        # Preparation for inference
        model, processor = self.model
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

    def get_durations(self, video_paths):
        durations = []
        for path in video_paths:
            try:
                container = av.open(path)
                # 时长 = 时基(time_base) * 总帧数
                stream = container.streams.video[0]
                duration_sec = float(stream.duration * stream.time_base)
            except Exception as e:
                print(f"Error reading {path}: {e}")
                duration_sec = 0.0
            durations.append(duration_sec)
        return durations

    def split_string_by_list(self, input_str, split_list):
        # 将分割列表中的元素拼接为一个正则表达式
        pattern = "|".join(map(re.escape, split_list))
        # 使用正则表达式分割字符串
        return re.split(pattern, input_str)

    def response2json(self, response_text, keys):
        extract_json = self.split_string_by_list(
            response_text, [f'"{key}":' for key in keys]
        )[1:]
        extract_json = [x.strip(" '\"\\\n{},") for x in extract_json]

        response_json = {key: extract_json[i] for i, key in enumerate(keys)}
        response_json = json.dumps(response_json)
        response_text = json.loads(response_json)
        return response_json

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
        主处理流程：
        1. 获取 clip 信息与描述
        2. 拼接连续 clip 对照图
        3. 调用模型生成 clip 之间差异描述
        4. 返回更新后的数据
        """

        self.get_model()

        video_path = data["path"]
        clip_dir_base = self.middel_result_save_dir
        frame_dir_base = self.middel_result_save_dir
        video_path_md5_hash = data["video_path_md5_hash"]
        clip_seq = data["clip_seq"]
        good_clips = data["good_clips"]
        seq_idx = data["seq_idx"]
        good_clip_idx = data["good_clip_idx"]
        response_singles = data["response_singles"]

        sample_save_dir = os.path.join(
            self.middel_result_save_dir, video_path_md5_hash, f"{seq_idx:05d}"
        )
        diff_paths = []
        frames = [
            [
                os.path.join(
                    sample_save_dir, f"video_{clip_idx:05d}", f"split_{i:05d}.jpg"
                )
                for i in range(3)
            ]
            for clip_idx in good_clip_idx
        ]
        for i in range(len(frames) - 1):
            pre_frame_list = frames[i]
            tail_frame_list = frames[i + 1]
            merged_frame_pair = self.get_merged_img_pad(
                [pre_frame_list, tail_frame_list]
            )
            diff_path = os.path.join(
                sample_save_dir,
                f"video_{good_clip_idx[i]:05d}",
                "merged_frame_pair.jpg",
            )
            merged_frame_pair.save(diff_path)
            diff_paths.append(diff_path)

        captions = self.cal_response_diff(response_singles, diff_paths)

        data["response_joint"] = captions
        return data
