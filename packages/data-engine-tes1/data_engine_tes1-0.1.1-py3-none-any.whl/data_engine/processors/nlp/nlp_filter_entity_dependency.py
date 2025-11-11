from functools import lru_cache
from data_engine.utils.model_utils import get_spacy_model
from data_engine.core.base import BaseFilter


class NlpFilterEntityDependency(BaseFilter):
    """
    文本蕴含关系复杂度
    用于过滤实体之间存在依存关系数量不足的文本样本。该过滤器基于 SpaCy 分析文本中名词类实体（包括名词、专有名词、代词）之间的依存关系，并计算实体之间存在依存关系的对数。
    如果依存关系数量低于设定阈值，则该文本将被过滤。
    该过滤器适用于结构简单、语义关联稀疏样本的筛除，常用于文本质量评估、抽取预筛、问答训练集构建等场景。
    """

    only_ray = True

    def __init__(
        self,
        lang: str = "zh",
        min_entity_dependency_count: int = 1,
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        lang: 语言类型 # ['zh', 'en'] # 指定文本语言类型，用于加载对应的 SpaCy 模型（中文或英文）
        min_entity_dependency_count: 最小实体依存关系数量 # [0, 正无穷] # 如果实体之间的依存关系数量小于该值，则该样本会被过滤
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.lang = lang
        self.min_entity_dependency_count = min_entity_dependency_count
        self.content = content

    def process(self, data):
        if self.lang == "zh":
            model = get_spacy_model("zh_core_web_sm")
        if self.lang == "en":
            model = get_spacy_model("en_core_web_sm")

        doc = model(data[self.content])
        entities = []
        entity_dependencies = {}
        entity_dependency_count = 0
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
                entity_dependencies[token] = []

        for entity in entities:
            for child in entity.children:
                if child in entities:  # 只考虑实体与实体之间的关系
                    entity_dependencies[entity].append(child)
                    entity_dependency_count += 1

        data["entity_dependency_count"] = entity_dependency_count

        if self.do_filter:
            if data["entity_dependency_count"] < self.min_entity_dependency_count:
                return {}
        return data
