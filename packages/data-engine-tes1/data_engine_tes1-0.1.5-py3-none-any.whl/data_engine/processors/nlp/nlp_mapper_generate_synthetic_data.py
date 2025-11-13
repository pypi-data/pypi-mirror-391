import os
import sys
import re
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))

# 将子目录添加到 sys.path
sys.path.append(current_dir)
import pandas as pd
from kg_rag.utility import *
from data_engine.core.base import BaseFilter, BaseMapper
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer, AutoModelForCausalLM
from data_engine.utils.model_utils import get_model_path


class NlpMapperGenerateSyntheticData(BaseMapper):
    """
    面向行业知识缺陷的针对性指令数据合成
    面向行业知识缺陷，合成针对性的指令数据，提升模型能力
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, temperature: float, **kwargs):
        """
        初始化方法：
            model_name_or_path:模型名称或地址#用于加载模型
            temperature:温度#控制的是模型生成文本时的随机性或多样性
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.temperature = temperature
        self.llm_model = None
        self.prompt = """For given facts, generate a question and its corresponding answer. The question should be designed to inquire about the relationship or classification described in the triples, and the answer should be an entity mentioned in the provided facts.\n\n
            Note:\n
            Generate only one question and answer in the style of the example below.\n
            Example:\n
            Facts:
            Disease <Thyroid Gland Mucoepidermoid Carcinoma> is a type of disease <thyroid gland carcinoma>.
            Compound <Liothyronine> treats disease <thyroid gland carcinoma>.
            Response:
            Question: What compound can be used to treat Thyroid Gland Mucoepidermoid Carcinoma?
            Answer: Liothyronine.

            Facts:
            Disease <thyroid gland carcinoma> resembles disease <ganglioneuroma> 
            Disease ganglioneuroma presents Symptom <Diarrhea>
            Response:
            Question: What symptom is associated with the disease that resembles thyroid gland carcinoma?
            Answer: Diarrhea.

            Facts: 
            Disease <head and neck cancer> resembles <thyroid gland carcinoma>.
            Disease <head and neck cancer> presents Symptom <Dysphonia>.
            Disease <head and neck cancer> presents Symptom <Neck Pain>.
            Disease <thyroid gland carcinoma> presents Symptom <Dysphonia>.
            Disease <thyroid gland carcinoma> presents Symptom <Neck Pain>.
            Compound <Paclitaxel> treats disease <head and neck cancer>.
            Response:
            Question: What disease is similar to thyroid gland carcinoma, with Symptom Dysphonia and Neck Pain.
            Answer: head and neck cancer.

            Facts:
            {}
            Response:
            """

    def _extract_question_and_answer(self, text):
        """
        从给定的文本中提取问题和答案。

        参数:
            text (str): 包含问题和答案的文本。

        返回:
            tuple: 包含问题和答案的元组 (question, answer)。
        """
        # 使用正则表达式匹配问题和答案
        pattern = r"Question: (.+?)\nAnswer: (.+)"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            question = match.group(1).strip()
            answer = match.group(2).strip()
            return question, answer
        else:
            return None, None

    def process(self, data):
        """
        基于知识图谱的大模型领域知识合成数据生成
        参数：
            mcts_path_ls: MCTS路径的列表
        """
        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path,
                gpu_memory_utilization=0.8,
                tensor_parallel_size=1,
                enforce_eager=True,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)

        set_seed(42)
        path = data["root"]
        evidences = []
        path_value = 0
        for node in path[0][1:]:
            node_value = node.value / (node.visits + 1)
            path_value += node_value
            sub = node.parent.state
            rel, obj = node.action
            sub = "<" + sub + ">"
            obj = "<" + obj + ">"
            prompt = rel.format(sub)
            case = prompt + " " + obj
            evidences.append(case)

        evidences_str = "\n".join(evidences)
        # single
        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant."},
            {"role": "user", "content": self.prompt.format(evidences_str)},
        ]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        sampling_params = SamplingParams(
            max_tokens=1024,
            seed=42,
        )
        sample = (
            self.llm_model.generate(formatted_prompt, sampling_params)[0]
            .outputs[0]
            .text
        )
        sample = re.sub(
            r"<\|start_header_id\|>assistant<\|end_header_id\|>", "", sample
        )
        question, answer = self._extract_question_and_answer(sample)
        print("Synthetic Dataset Generated Done!")
        data.pop("root")
        data["question"] = question
        data["answer"] = answer
        data["evidence"] = evidences_str
        data["value"] = path_value
        print(data)
        return data
