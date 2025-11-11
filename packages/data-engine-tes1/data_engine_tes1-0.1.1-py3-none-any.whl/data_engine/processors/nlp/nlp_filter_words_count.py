from functools import lru_cache
from data_engine.utils.model_utils import get_spacy_model
from data_engine.core.base import BaseFilter


class NlpFilterWordsCount(BaseFilter):
    """
    词数过滤器
    用于过滤文本中词语数量不足的样本。通过 SpaCy 模型对文本进行分词并统计词语总数，判断是否达到设定的最小词数阈值。
    """

    only_ray = True

    def __init__(
        self,
        lang: str = "zh",
        min_words_count: int = 10,
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        lang: 语言类型#['zh', 'en']#支持 'zh'（中文）或 'en'（英文）。用于加载相应的 SpaCy 模型
        min_words_count: 最小词数阈值#用于过滤词语数量低于此阈值的文本
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.lang = lang
        self.action_poss = ["VERB"]
        self.min_words_count = min_words_count
        self.content = content

    def process(self, data):
        if self.lang == "zh":
            model = get_spacy_model("zh_core_web_sm")
        elif self.lang == "en":
            model = get_spacy_model("en_core_web_sm")

        doc = model(data[self.content])
        words = [token.text for token in doc]
        total_words = len(words)
        data["words_count"] = total_words

        if self.do_filter:
            if data["words_count"] < self.min_words_count:
                return {}
        return data
