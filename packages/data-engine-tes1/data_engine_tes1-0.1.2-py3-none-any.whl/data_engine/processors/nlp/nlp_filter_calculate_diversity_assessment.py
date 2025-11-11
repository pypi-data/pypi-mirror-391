from data_engine.core.base import BaseFilter
import re
from tqdm import tqdm
import nltk
import jieba
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import numpy as np


class NlpFilterCalculateDiversityAssessment(BaseFilter):
    """
    指令数据集多样性评估
    通过计算MTLD评估指令数据集的多样性
    后训练数据合成专用算法
    """

    only_ray = True

    def __init__(self, **kwargs):
        """
        初始化方法:
        """
        super().__init__(**kwargs)

    # 函数：计算MTLD（Multilevel Textual Diversity）
    def _mtld(self, text):
        tokens = jieba.lcut(text.lower())
        types = set(tokens)
        total_tokens = len(tokens)
        type_token_ratio = len(types) / total_tokens
        return 1 / type_token_ratio

    def process(self, data: dict):
        full_text = " ".join([j["content"] for j in data["content"]])
        data["mtld"] = self._mtld(full_text)
        return data
