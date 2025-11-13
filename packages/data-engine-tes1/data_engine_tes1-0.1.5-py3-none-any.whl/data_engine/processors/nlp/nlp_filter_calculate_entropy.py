from data_engine.core.base import BaseFilter
import re
from tqdm import tqdm
import jieba
import math
from collections import Counter


class NlpFilterCalculateEntropy(BaseFilter):
    """
    指令数据集信息量评估
    通过计算指令数据集的信息量用于评估对于理解数据的复杂性、预测模型的潜在性能以及优化数据处理策略
    后训练数据合成专用算法
    """

    only_ray = True

    def __init__(self, **kwargs):
        """
        初始化方法:
        """
        super().__init__(**kwargs)

    def process(self, data: dict):

        full_text = " ".join([j["content"] for j in data["content"]])
        words = jieba.lcut(full_text)
        if not words:
            data["meta"]["entropy"] = 0.0

        word_counts = Counter(words)
        total_words = len(words)

        entropy = 0.0
        for count in word_counts.values():
            probability = count / total_words
            if probability > 0:
                entropy -= probability * math.log2(probability)
        data["entropy"] = entropy
        return data
