import json
import jieba
import re
from typing import List, Dict
from data_engine.core.base import BaseFilter


class NlpFilterStopWords(BaseFilter):
    """
    停用词比例
    用于根据文本中的中英文停止词比例过滤样本，是一个结合中文分词与简单文本清洗的过滤器。其核心逻辑是计算输入文本中停止词的比例，并根据设定的最大阈值进行过滤。
    """

    def __init__(
        self,
        max_ratio: float = 0.3,
        use_words_aug: bool = False,
        stopwords_list: List[str] = [
            "的",
            "了",
            "和",
            "是",
            "在",
            "就",
            "都",
            "而",
            "及",
            "与",
        ],
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        max_ratio: 停止词比例阈值#[0, 1]#文本中停止词比例若高于该值，则会被过滤
        use_words_aug: 是否使用词增强#是否启用词增强功能，与其他模块兼容的预留参数
        stopwords_list: 停止词列表#用户直接提供的停止词列表，用于补充或替代停止词文件
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.max_ratio = max_ratio
        self.use_words_aug = use_words_aug
        self.stopwords = set(stopwords_list)
        self.content = content

    def _tokenize_and_calc_ratio(self, text: str) -> float:
        # 清洗文本（包括中文标点、特殊符号）
        clean_text = re.sub(r"[^\w\u4e00-\u9fff]", " ", text)
        clean_text = re.sub(r"\s+", " ", clean_text)

        # 中文分词
        words = jieba.lcut(clean_text)
        words = [w.lower() for w in words if w.strip()]
        if not words:
            return 0.0
        stopword_count = sum(1 for word in words if word in self.stopwords)
        return stopword_count / len(words)

    def process(self, data):
        text = data[self.content]
        ratio = self._tokenize_and_calc_ratio(text)
        data["stopword_ratio"] = ratio
        if self.do_filter and ratio >= self.max_ratio:
            return {}
        return data
