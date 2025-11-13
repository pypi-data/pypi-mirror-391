from data_engine.core.base import BaseFilter
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import re
from tqdm import tqdm
from data_engine.utils.model_utils import get_model_path


class NlpFilterEvolFilter(BaseFilter):
    """
    进化校验:
    校验进化算法是否按照要求合成数据
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, **kwargs):
        """
        初始化方法：
            model_name_or_path:大模型的名字或路径#用于加载模型
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.comparison_instruction = "Here are two Instructions to ChatGPT AI, do you think they are equal to each other, which meet the following requirements:\r\n\
					1. They have same constraints and requirements.\r\n\
					2. They have same depth and breadth of the inquiry.\r\n\
					The First Prompt: <Here is first instruction.>\r\n\
					The Second Prompt: <Here is second instruction.>\r\n\
					Your Judgement (Just answer: Equal or Different. No need to explain the reason.):\r\n"
        self.llm_model = None

    def _createComparisonEliminatorPrompt(self, before, after):
        prompt = self.comparison_instruction
        prompt = prompt.replace("<Here is first instruction.>", before)
        prompt = prompt.replace("<Here is second instruction.>", after)
        return prompt

    def process(self, data: dict):

        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path, tensor_parallel_size=1, enforce_eager=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)

        instruction = data["content"][0]["content"]
        evol_instruction = data["evol"][0]["content"]

        prompt = self._createComparisonEliminatorPrompt(instruction, evol_instruction)

        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant."},
            {"role": "user", "content": prompt},
        ]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        sampling_params = SamplingParams(
            max_tokens=2048,
            seed=42,
        )
        result = (
            self.llm_model.generate(formatted_prompt, sampling_params)[0]
            .outputs[0]
            .text
        )
        if "equal" in result.lower():
            data["retain"] = False
        else:
            data["retain"] = True
        return data
