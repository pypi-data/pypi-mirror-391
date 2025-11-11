import json
import time, torch
from PIL import Image
import os
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
import re
from data_engine.core.base import BaseFilter
from data_engine.utils.model_utils import get_model_path


class VideoMapperClipSeqSingleAnnotation(BaseFilter):
    """
    基于视频切片的单独描述生成
    用途：对筛选出来的 clip 序列生成详细描述，帮助盲人理解视频片段。

    主要流程：
    1. 抽取各 clip 中对应帧并拼接成单个文件
    2. 使用 Qwen 大模型对拼接后的图像生成描述
    3. 结构化描述成 JSON 格式，包括 video_content、camera_angle、camera_movement、video_background 四部分
    交错视频工作流专用算法
    交错视频所有的中间结果目录需要设置为相同的目录
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(
        self,
        model_name_or_path: str,
        middel_result_save_dir: str = None,
        min_pixels: int = 200704,
        max_pixels: int = 1003520,
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

    def cal_response_single(self, sin_paths):
        """
        对一批 clip 序列生成描述
        Args:
            sin_paths (List[Tuple[frame_list, num_seconds]])
        Returns:
            List[str]: 模型描述结果
        """
        response_texts = []
        for i, sin_path in enumerate(sin_paths[:]):
            frames, num_seconds = sin_paths[i]
            content = []
            prompt_single = {
                "type": "text",
                "text": f"""
                                You are the most powerful video understanding model which is responsible for generation video description to help the blind people to understand the video. Since they cannot see, you should describe the video as detailed as possible.
                                You will see some consecutive frames extracted evenly from the video. The total number of frames in the video is 3,  and the total duration of the video is {num_seconds:.2f} seconds.
                                **Description Hints**:
                                - If the video is focused on a specific subject, please provide detailed descriptions of the subject's textures, attributes, locations, presence, status, characteristics, countings, etc. If there are multiple subjects, please accurately describe their relationships with each other.
                                - Summarize the possible types of current video. You can refer to: landscape videos, aerial videos, action videos, documentaries, educational videos, product promotional videos/advertisements, slow-motion videos, time-lapse videos, music videos/MVs, interview videos, animations, movie clips, How-To videos, and so on.
                                - If there are commen sense or world knowledge, for example, species, celebrities, scenic spots and historical sites, you must state them explicitly instead of using phrases like "a person", "a place", etc.
                                - If there is any textual information in the video, describe it in its original language without translating it.
                                - If there are any camera movements, please describe them in detail. You may refer to professional photography terms like "Pan" "Tilt" "follow focus" "multiple angles", but remember only state them when you're absolutely sure. DO NOT make up anything you don't know.
                                - Include temporal information in the description of the video.
                                - Scene transitions: For example, transitioning from indoors to outdoors, or from urban to rural areas. This can be indicated by specifying specific time points or using transition sentences.
                                - Progression of events: Use time-order words such as "first," "then," "next," "finally" to construct the logical sequence of events and the flow of time.
                                - Use verbs and adverbs to describe the speed, intensity, etc., of actions, such as "walking slowly," "suddenly jumping."
                                - Facial expressions and emotional changes: Capture facial expressions of characters, such as "frowning," "smiling."
                                - Whether the video is in slow motion or fast motion: Determine and indicate whether the video is in slow motion or accelerated.
                                - Any other temporal information you can think of.
                                **Restriction Policies**:
                                - The description should be purely factual, with no subjective speculation.
                                - DO NOT add any unnecessary speculation about the things that are not part of the video such as "it is inspiring to viewers" or "seeing this makes you feel joy".
                                - DO NOT add the evidence or thought chain. If there are some statement are inferred, just state the conclusion.
                                - DO NOT add things such as "creates a unique and entertaining visual" "creating a warm atmosphere" as these descriptions are interpretations and not a part of the video itself.
                                - DO NOT analyze the text content in the video, and only tell the content themselves.
                                - DO NOT include words like "image" "frame" "sequence" "video" "visuals" "content" in your response.  Describe only and directly content and events.
                                - Do NOT use words like 'series of shots', 'sequence', 'scene', 'video', 'frame', 'image', 'visuals', 'content' as the subject of description; directly describe the content of the video.
                                - DO NOT describe frame by frame, or use "first frame" "second frame". Describe the video as a whole directly.
                                - DO NOT analyze, subjective interpretations, aesthetic rhetoric, such as context, atmosphere, suggest, drama, etc. focus solely on objective descriptions.
                                - DO NOT including any reasoning description like "probably because" or "appears to be".
                                **Description Requirment**:
                                Please describe the video by:
                                1) the video content: comprehensive description of the video content, encompassing key actions, the unfolding plot, characters, objects, and visual details. This includes describing the movement and behavior of the characters, the progression of the narrative, and how objects or settings are used within the story. Additionally, highlight any relevant visual or thematic elements that contribute to the overall tone and message of the video. This analysis should consider how all these components work together to enhance the viewer's understanding and experience of the scene.（about 300 words）                            
                                2) the camera angle: the perspective from which the camera captures the main object or scene. （about 30 words）
                                3) the camera movement: panning, tilting, and tracking, as well as changes in zoom (in or out) and focus.（about 30 words）                           
                                4) the background: the environmental factors, lighting, space, surrounding elements that provide context to the scene, and the setting in which the action unfolds.（about 60 words）
                                Do not analyze, subjective interpretations, aesthetic rhetoric, such as "context", "atmosphere", "suggest", "drama", etc. focus solely on objective descriptions.
                                DO not including any reasoning description like "suggest", "indicate", "probably because", "appears to be".
                                Note that the consecutive frames reflect the passage of time, so the video can be described along the timeline.
                                Directly return in the json format like this:
                                {{"video_content": "...", "camera_angle": "...", "camera_movement": "...",  "video_background": "...", }}.  
                                #[Video Frames]: 
                                """,
            }

            content.append(prompt_single)
            content = self.add_img(
                frames,
                content,
            )

            messages = [{"role": "user", "content": content}]

            retries = 0
            max_retries = 1
            retry_delay = 10

            while retries < max_retries:
                try:
                    response_text = self.cal_qwen(messages)
                    # response_text = self.response2json(response_text, ["video_content", "camera_angle", "camera_movement", "video_background"])
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
        """将图片路径添加为消息中 image 类型"""
        # imgs = [code_img(img) for img in imgs]

        for i, img in enumerate(imgs):
            content.append(
                {
                    "type": "image",
                    "image": img,
                }
            )
        return content

    def cal_qwen(self, messages):
        """
        模型推理逻辑：
        Args:
            messages: 对话消息列表
        Returns:
            模型生成结果字符串
        """
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
        """
        获取视频时长
        Args:
            video_paths: 视频文件路径列表
        Returns:
            durations: 每个视频对应时长（float 秒）
        """
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
        主处理逻辑：
        1. 获取模型
        2. 抽取对应 clip 中所有帧的拼接图片
        3. 对拼接图片调用大模型生成描述
        4. 把描述更新到 data 中
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

        sample_save_dir = os.path.join(
            self.middel_result_save_dir, video_path_md5_hash, f"{seq_idx:05d}"
        )

        duration_list = self.get_durations(good_clips)
        frame_list = [
            [os.path.join(sample_save_dir, f"video_frames_{clip_idx:05d}.jpg")]
            for clip_idx in good_clip_idx
        ]

        sin_paths = [
            (frame, duration) for frame, duration in zip(frame_list, duration_list)
        ]
        captions = self.cal_response_single(sin_paths)

        data["response_singles"] = captions
        return data
