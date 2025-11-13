import sys
from data_engine.core.base import Base, BaseProcessor, BaseFilter


class NlpFilterAvgLineLength(BaseFilter):
    """
    平均行长度过滤器
    用于过滤文本中平均行长度不在指定范围内的样本。该过滤器会将输入文本按行拆分，计算所有行的平均长度，
    并根据设定的最小（min_len）和最大（max_len）阈值判断是否保留该样本。
    若平均行长度小于最小值或大于最大值，则该样本会被过滤
    """

    def __init__(
        self, min_len: int = 10, max_len: int = 1000000, content: str = "text", **kwargs
    ):
        """
        初始化方法

        min_len: 最小平均行长度 #样本中所有行的平均长度若小于该值，则该样本会被过滤
        max_len: 最大平均行长度 #样本中所有行的平均长度若大于该值，则该样本会被过滤
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.min_len = min_len
        self.max_len = max_len
        self.content = content

    def process(self, data):
        lines = data[self.content].splitlines()
        line_lengths = list(map(len, lines)) or [0]
        avg_length = sum(line_lengths) / len(line_lengths) if lines else 0
        data["avg_line_length"] = avg_length

        if self.do_filter and not (self.min_len <= avg_length <= self.max_len):
            return {}
        return data
