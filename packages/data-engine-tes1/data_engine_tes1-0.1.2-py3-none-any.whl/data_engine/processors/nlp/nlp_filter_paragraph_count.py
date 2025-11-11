from data_engine.core.base import BaseFilter


class NlpFilterParagraphCount(BaseFilter):
    """
    段落数量
    用于过滤文本中段落数量不足的样本。通过将输入文本按换行符分割成段落，分析非空白段落数量，并根据设定的最小阈值进行过滤。
    """

    def __init__(self, min_paragraphs_count: int = 1, content: str = "text", **kwargs):
        """
        初始化方法
        min_paragraphs_count: 最小段落数量# 要求的最小段落数量。若文本中段落数量小于该值，则文本会被过滤。
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.min_paragraphs_count = min_paragraphs_count
        self.content = content

    def process(self, data: dict) -> dict:
        # 将文本按换行符分割，过滤掉全是空白的段落
        paragraphs = [para for para in data[self.content].split("\n") if para.strip()]
        data["paragraphs_count"] = len(paragraphs)

        if self.do_filter:
            if data["paragraphs_count"] < self.min_paragraphs_count:
                return {}
        return data
