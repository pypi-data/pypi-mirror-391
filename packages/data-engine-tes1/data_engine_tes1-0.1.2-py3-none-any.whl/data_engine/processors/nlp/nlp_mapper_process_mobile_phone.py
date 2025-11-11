from data_engine.core.base import BaseFilter, BaseMapper
import re
from tqdm import tqdm


class NlpMapperProcessMobilePhone(BaseMapper):
    """
    手机号脱敏
    该算子是一种高效的文本处理工具，专门设计用于从大量文本数据中快速、准确地识别出手机号。
    """

    def __init__(
        self, content: str = "text", special_token: str = "__replace__", **kwargs
    ):
        """
        初始化方法：
            content:文本#数据中待识别文本的字段名称
            special_token:特殊字符#数据中用于替换敏感信息的字符
        """
        super().__init__(**kwargs)
        self.content = content
        self.special_token = special_token

    def process(self, data: dict):

        text = data[self.content]
        pattern = r"(?:\D|^)1[3-9]\d{9}(?:\D|$)"
        phone_numbers = re.findall(pattern, text, re.DOTALL)
        phone_numbers = [re.sub(r"\D", "", num) for num in phone_numbers]
        for item in phone_numbers:
            text = re.sub(item, self.special_token, text)
        data[self.content] = text
        return data
