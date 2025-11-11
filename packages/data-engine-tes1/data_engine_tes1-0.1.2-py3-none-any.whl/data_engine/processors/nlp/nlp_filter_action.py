from data_engine.utils.model_utils import get_spacy_model
from data_engine.core.base import BaseFilter


class NlpFilterAction(BaseFilter):
    """
    执行动词数量
    用于过滤文本中包含“动词”数量不足的样本，是一个基于 SpaCy 的动词识别过滤器。其核心逻辑是分析输入文本中动词（POS 标签为 'VERB'）的数量，并根据设定的最小阈值进行过滤。
    """

    only_ray = True

    def __init__(
        self, lang: str = "zh", min_action_num: int = 1, content: str = "text", **kwargs
    ):
        """
        初始化方法
        lang: 语言类型#['zh', 'en']#支持 'zh'（中文）或 'en'（英文）。用于加载相应的 SpaCy 模型
        min_action_num: 最小动词数量阈值#若文本中动词数量小于该值，则文本会被过滤
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.lang = lang
        self.action_poss = ["VERB"]
        self.min_action_num = min_action_num
        self.content = content

    def process(self, data):
        if self.lang == "zh":
            model = get_spacy_model("zh_core_web_sm")
        elif self.lang == "en":
            model = get_spacy_model("en_core_web_sm")

        doc = model(data[self.content])
        num_action = 0
        word_cnt = 0
        for token in doc:
            word_cnt += 1
            if token.pos_ in self.action_poss:
                num_action += 1
        data["num_action"] = num_action

        if self.do_filter:
            if data["num_action"] < self.min_action_num:
                return {}
        return data
