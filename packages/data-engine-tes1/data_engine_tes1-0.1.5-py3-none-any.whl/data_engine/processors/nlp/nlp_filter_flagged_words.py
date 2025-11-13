import json
import jieba
import re
from typing import List, Dict
from data_engine.core.base import BaseFilter


class NlpFilterFlaggedWords(BaseFilter):
    """
    毒性字符占比
    用于过滤文本中包含敏感词比例过高的样本。该过滤器支持通过外部文件或直接传参的方式加载敏感词列表，并结合 Jieba 分词，对输入文本进行分词统计敏感词比例。若敏感词比例超过设定阈值，则过滤该样本。
    """

    def __init__(
        self,
        max_ratio: float = 0.1,
        use_words_aug: bool = False,
        sensitive_words: List[str] = [
            "赌博",
            "色情",
            "诈骗",
            "毒品",
            "暴力",
            "恐怖",
            "黑客",
            "洗钱",
            "假证",
            "走私",
        ],
        text_field: str = "text",
        **kwargs
    ):
        """
        初始化方法
        max_ratio: 敏感词比例最大阈值 #[0, 1]#若文本中敏感词所占比例大于该值，则文本会被过滤
        use_words_aug: 是否启用词表增强#预留参数，用于扩展词表增强功能，目前未启用
        sensitive_words: 敏感词列表#可直接传入敏感词列表，优先级高于文件内容，可与文件内容合并使用
        text_field: 文本字段名#指定待处理数据中用于分析的文本字段名称
        """
        super().__init__(**kwargs)
        self.max_ratio = max_ratio
        self.use_words_aug = use_words_aug
        self.text_field = text_field
        self.sensitive_words = set(sensitive_words)

    def _tokenize_and_calc_ratio(self, text: str) -> float:
        # 文本清洗
        clean_text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", " ", text)
        clean_text = re.sub(r"\s+", " ", clean_text)

        words = jieba.lcut(clean_text, HMM=False)
        words = [w.lower() for w in words if w.strip()]
        if not words:
            return 0.0

        sensitive_count = sum(1 for word in words if word in self.sensitive_words)
        return sensitive_count / len(words)

    def process(self, data: Dict) -> Dict:
        text = data.get(self.text_field, "")
        ratio = self._tokenize_and_calc_ratio(text)
        data["sensitive_ratio"] = ratio
        if self.do_filter and ratio >= self.max_ratio:
            return {}
        return data
