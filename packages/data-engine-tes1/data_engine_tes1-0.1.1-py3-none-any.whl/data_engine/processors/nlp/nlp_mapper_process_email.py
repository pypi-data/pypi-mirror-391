from data_engine.core.base import BaseFilter, BaseMapper
import re
from tqdm import tqdm


class NlpMapperProcessEmail(BaseMapper):
    """
    电子邮箱脱敏
    该算子是一种高效的文本处理工具，专门设计用于从大量文本数据中快速、准确地识别出电子邮箱地址。
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
        pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

        matches = re.findall(pattern, text, re.DOTALL)
        # data["sensitive_information_email"] = matches
        for item in matches:
            text = re.sub(re.escape(item), self.special_token, text)
        data[self.content] = text
        return data
