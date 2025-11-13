from data_engine.core.base import BaseFilter
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import re
from tqdm import tqdm
import numpy as np
from data_engine.utils.model_utils import get_model_path


class NlpFilterCalculateLossSingle(BaseFilter):
    """
    指令数据集损失值计算
    在指令数据集中，损失值可以帮助我们了解模型对指令的理解和执行能力是否准确。通过计算损失值，我们可以评估数据集的质量，发现数据中存在的问题（如噪声、标注错误等），并优化数据集以提高模型的性能。
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, **kwargs):
        """
        初始化方法：
            model_name_or_path: 模型的名字或路径#用于加载模型
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)

        self.llm_model = None

    def process(self, data: dict):

        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path, tensor_parallel_size=1, enforce_eager=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)

        full_text = " ".join([j["content"] for j in data["content"]])

        sampling_params = SamplingParams(
            temperature=1.0, max_tokens=1, logprobs=1, prompt_logprobs=True
        )
        outputs = self.llm_model.generate([full_text], sampling_params)
        output = outputs[0]
        if hasattr(output, "prompt_logprobs") and output.prompt_logprobs:
            log_probs = []
            for token_logprobs in output.prompt_logprobs:
                if token_logprobs:

                    for token_id, logprob_info in token_logprobs.items():
                        log_probs.append(logprob_info.logprob)
                        break

            if log_probs:
                avg_nll = -np.mean(log_probs)

        data["loss"] = avg_nll
        return data
