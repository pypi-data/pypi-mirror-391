import sys
from data_engine.core.base import Base, BaseProcessor, BaseFilter


class NlpFilterMaxLineLength(BaseFilter):
    """
    最大行长度过滤器
    用于过滤文本中行长度不符合要求的样本。通过分析每行文本的最大长度，判断其是否在设定的最小和最大范围内，超出范围的文本将被过滤。
    """

    def __init__(
        self, min_len: int = 10, max_len: int = 1000000, content: str = "text", **kwargs
    ):
        """
        初始化方法
        min_len: 最小行长度# 样本中行长度的下限，若行的最大长度小于此值，则样本会被过滤
        max_len: 最大行长度# 样本中行长度的上限，若行的最大长度超过此值，则样本会被过滤
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.min_len = min_len
        self.max_len = max_len
        self.content = content

    def process(self, data):
        lines = data[self.content].splitlines()
        line_lengths = list(map(len, lines)) or [0]
        data["max_length"] = max(line_lengths)
        if self.do_filter:
            if data["max_length"] < self.min_len or data["max_length"] > self.max_len:
                return {}

        return data
