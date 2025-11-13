from data_engine.core.base import BaseFilter


class NlpFilterAlphanumeric(BaseFilter):
    """
    字母数字占比过滤器
    用于过滤字母/数字占比不符合要求的文本样本。该过滤器通过统计文本中属于字母或数字的字符数量，
    计算其在总字符数中的占比（即 alphanumeric ratio），并依据设定的最小和最大阈值进行过滤。
    如果比例小于最小阈值或大于最大阈值，则该样本会被过滤掉
    """

    def __init__(
        self,
        min_ratio: float = 0.25,
        max_ratio: float = 1.0,
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        min_ratio: 最小字母数字比# [0.0, 1.0]# 用于设定文本中字母/数字最小占比阈值，低于该值的样本会被过滤
        max_ratio: 最大字母数字比# [0.0, 1.0]# 用于设定文本中字母/数字最大占比阈值，高于该值的样本会被过滤
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.content = content

    def process(self, data):
        # 仅包含英文和数字（排除中文等非ASCII字符）
        alnum_count = sum(
            map(
                lambda char: 1 if char.isascii() and char.isalnum() else 0,
                data[self.content],
            )
        )
        data["alnum_ratio"] = (
            (alnum_count / len(data[self.content]))
            if len(data[self.content]) != 0
            else 0.0
        )
        if self.do_filter:
            if (
                data["alnum_ratio"] < self.min_ratio
                or data["alnum_ratio"] > self.max_ratio
            ):
                return {}
        return data
