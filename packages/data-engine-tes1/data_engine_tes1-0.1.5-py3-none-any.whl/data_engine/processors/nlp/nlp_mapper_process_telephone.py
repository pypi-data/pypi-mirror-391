from data_engine.core.base import BaseFilter, BaseMapper
import re
from tqdm import tqdm


class NlpMapperProcessTelephone(BaseMapper):
    """
    电话号脱敏
    该算子是一种高效的文本处理工具，专门设计用于从大量文本数据中快速、准确地识别出电话号码。
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

    def extract_phone_numbers(self, text):
        # 综合电话号码匹配模式
        phone_pattern = r"""
            (?:
                # 国际电话号码格式 +X-XXX-XXX-XXXX 等
                \+\d{1,3}[-\s]?\(?\d{1,4}\)?[-\s]?\d{3,4}[-\s]?\d{3,4}[-\s]?\d{0,4} |
                # 中国手机号码
                (?:\+86[-\s]?)?1[3-9]\d{9} |
                # 固定电话（支持全角和半角括号）
                (?:[\(（]\d{3,4}[\)）]|\d{3,4}[-\s]?)\d{7,8}(?:[-\s]?(?:ext|分机)\.?\s*\d{1,5})? |
                # 400/800 热线
                (?:400|800)[-\s]?\d{3}[-\s]?\d{4} |
                # 国际格式如 0207-123-4567, 202-555-0147
                \b\d{3,5}[-\s]\d{3}[-\s]\d{4}\b |
                # 特殊服务号码（明确列出）
                (?<!\d)(?:110|119|120|122|12315|12306|12345|12121|12117|95598|95588|95533|95555|95338|95311|95583|95530|9510211|10000|10086|10010|114)(?!\d)
            )
            (?!\d)  # 确保后面没有数字
        """

        # 编译电话号码正则表达式
        phone_regex = re.compile(phone_pattern, re.VERBOSE)

        # 不应被识别为电话的模式
        exclude_patterns = [
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP地址
            r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{4,5}[A-Z0-9挂学警港澳]?",  # 车牌号
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 邮箱
            r"(?:身份证|证件号|ID|fake\s+id)",  # 身份证相关内容
            r"\b\d{16,}\b",  # 过长的数字串
        ]

        # 首先检查整个文本是否包含需要排除的内容
        should_exclude_text = False
        for pattern in exclude_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                should_exclude_text = True
                break

        phones = []
        # 如果文本不包含排除内容，则查找电话号码
        if not should_exclude_text:
            # 查找所有匹配的电话号码
            for match in phone_regex.finditer(text):
                phone = match.group()
                phones.append(phone)

        # return list(dict.fromkeys(phones))
        return phones

    def process(self, data: dict):
        text = data[self.content]
        phone_numbers = self.extract_phone_numbers(text)
        for item in phone_numbers:
            text = re.sub(re.escape(item), self.special_token, text)
        data[self.content] = text
        return data
