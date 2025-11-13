import langid
import numpy as np
from data_engine.core.base import Base, BaseProcessor, BaseFilter


class NlpFilterLanguageScoreFilter(BaseFilter):
    """
    语言分类即置信度得分
    用于过滤文本中指定语言的置信度分数低于设定最小值的样本。基于 `langid` 实现语言类型识别和置信度计算。
    """

    def __init__(self, lang: str = None, min_score: float = 0.8, **kwargs):
        """
        初始化方法
        lang: 语言类型#['zh', 'en']#当启用过滤时，用于指定需要保留的目标语言类型（如 'zh', 'en'）
        min_score: 最小置信度分数#[0, 1]#若语言置信度分数低于该值，则样本会被过滤
        """
        super().__init__(**kwargs)
        self.lang = lang
        self.min_score = min_score

    def process(self, data):
        scores = langid.rank(data["text"])  # [(lang, loglike), ...]
        langs, logs = zip(*scores)
        logs = np.array(logs, dtype=float)
        # 减去最大值防止下溢，再softmax
        logs -= logs.max()
        probs = np.exp(logs)
        probs /= probs.sum()
        # 取最大概率
        idx = probs.argmax()

        data["lang_type"] = langs[idx]
        data["lang_score"] = float(probs[idx])
        if self.do_filter:
            if data["lang_score"] < self.min_score or data["lang_type"] != self.lang:
                return {}
        return data
