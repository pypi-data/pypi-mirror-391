from data_engine.core.base import BaseFilter, BaseMapper
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import re
from tqdm import tqdm
import random
from data_engine.utils.model_utils import get_model_path


class NlpMapperInstructionEvol(BaseMapper):
    """
    基于进化算法的数据合成
    利用进化算法的从深度和广度等角度合成数据方法
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, **kwargs):
        """
        初始化方法：
            model_name_or_path: 大模型的名字或路径#用于加载模型
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.base_instruction_breadth = "I want you act as a Prompt Creator.\r\n\
        Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.\r\n\
        This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.\r\n\
        The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.\r\n\
        The #Created Prompt# must be reasonable and must be understood and responded by humans.\r\n\
        '#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#\r\n"

        self.base_instruction_depth = "I want you act as a Prompt Rewriter.\r\n \
        Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.\r\n \
        But the rewritten prompt must be reasonable and must be understood and responded by humans.\r\n \
        Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#. \r\n \
        You SHOULD complicate the given prompt using the following method: \r\n\
        {} \r\n\
        You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#. \r\n\
        '#The Given Prompt#', '#Rewritten Prompt#', 'given prompt' and 'rewritten prompt' are not allowed to appear in #Rewritten Prompt#\r\n"

        self.llm_model = None

    def _createBreadthPrompt(self, instruction):
        prompt = self.base_instruction_breadth
        prompt += "#Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Created Prompt#:\r\n"
        return prompt

    def _createConstraintsPrompt(self, instruction):
        prompt = self.base_instruction_depth.format(
            "Please add one more constraints/requirements into #The Given Prompt#'"
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def _createDeepenPrompt(self, instruction):
        prompt = self.base_instruction_depth.format(
            "If #The Given Prompt# contains inquiries about certain issues, the depth and breadth of the inquiry can be increased."
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def _createConcretizingPrompt(self, instruction):
        prompt = self.base_instruction_depth.format(
            "Please replace general concepts with more specific concepts."
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def _createReasoningPrompt(self, instruction):
        prompt = self.base_instruction_depth.format(
            "If #The Given Prompt# can be solved with just a few simple thinking processes, you can rewrite it to explicitly request multiple-step reasoning."
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def process(self, data: dict):

        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path, tensor_parallel_size=1, enforce_eager=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)

        instruction = data["content"][0]["content"]
        evol_prompts = []
        evol_prompts.append(self._createBreadthPrompt(instruction))
        evol_prompts.append(self._createConstraintsPrompt(instruction))
        evol_prompts.append(self._createDeepenPrompt(instruction))
        evol_prompts.append(self._createConcretizingPrompt(instruction))
        evol_prompts.append(self._createReasoningPrompt(instruction))
        selected_evol_prompt = random.choice(evol_prompts)

        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant."},
            {"role": "user", "content": selected_evol_prompt},
        ]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        result = self.llm_model.generate(formatted_prompt)[0].outputs[0].text
        data["evol"] = [{"role": "user", "content": result}]

        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant."},
            {"role": "user", "content": result},
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
        data["evol"].append({"role": "assistant", "content": result})

        return data
