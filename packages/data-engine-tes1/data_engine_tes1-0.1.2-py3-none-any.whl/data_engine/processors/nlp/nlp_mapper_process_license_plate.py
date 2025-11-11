from data_engine.core.base import BaseFilter, BaseMapper
import re
from tqdm import tqdm


class NlpMapperProcessLicensePlate(BaseMapper):
    """
    车牌号脱敏
    该算子是一种高效的文本处理工具，专门设计用于从大量文本数据中快速、准确地识别出车牌号。
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
        # pattern = r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{4}[A-Z0-9挂学警港澳]"
        pattern = r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][·]?[A-Z0-9]{4}[A-Z0-9挂学警港澳]"

        matches = re.findall(pattern, text, re.DOTALL)
        for item in matches:
            text = re.sub(re.escape(item), self.special_token, text)
        data[self.content] = text
        return data
