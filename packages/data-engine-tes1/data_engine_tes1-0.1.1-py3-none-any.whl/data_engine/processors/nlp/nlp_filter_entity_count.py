from functools import lru_cache
from data_engine.utils.model_utils import get_spacy_model
from data_engine.core.base import BaseFilter


class NlpFilterEntityCount(BaseFilter):
    """
    实体数量
    用于过滤文本中名词类实体数量不足的样本，是一个基于 SpaCy 的实体识别过滤器。
    核心逻辑是分析输入文本中名词、专有名词和代词等实体的数量，并根据设定的最小阈值进行过滤。
    该过滤器适用于中英文文本，支持基于词性（POS）和详细词性标签（TAG）的双重判断。
    """

    only_ray = True

    def __init__(
        self,
        lang: str = "zh",
        min_entity_count: int = 1,
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        lang: 语言类型 # ['zh', 'en'] # 支持 'zh'（中文）或 'en'（英文），用于加载相应的 SpaCy 模型
        min_entity_count: 最小实体数量阈值 # 若文本中识别出的名词类实体数量小于该值，则该样本会被过滤
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.lang = lang
        self.min_entity_count = min_entity_count
        self.content = content

    def process(self, data):
        if self.lang == "zh":
            model = get_spacy_model("zh_core_web_sm")
        if self.lang == "en":
            model = get_spacy_model("en_core_web_sm")

        doc = model(data[self.content])
        entities = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN", "PRON"] and token.tag_ in [
                "NN",
                "NR",
                "PN",
                "NNS",
                "NNP",
                "NNPS",
                "PRP",
            ]:
                entities.append(token)
        data["entity_count"] = len(entities)

        if self.do_filter:
            if data["entity_count"] < self.min_entity_count:
                return {}
        return data
