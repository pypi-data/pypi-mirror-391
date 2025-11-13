from data_engine.core.base import BaseFilter, BaseMapper
import re
from tqdm import tqdm


class NlpMapperProcessIPAddress(BaseMapper):
    """
    IP地址清理
    该算子是一种高效的文本处理工具，专门设计用于从大量文本数据中快速、准确地识别出IP地址。
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
        # pattern = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"

        # 预编译正则表达式
        import re

        ipv4_pattern = re.compile(
            r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        )

        # 简化的IPv6正则表达式
        # 覆盖大多数常见格式，减少分支数量
        ipv6_pattern = re.compile(
            r"(?:"
            # 完整8组格式
            r"[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){7}" r"|"
            # 包含双冒号的压缩格式
            r"(?:[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,6})?"
            r"::"
            r"(?:[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,6})?"
            r")",
            re.IGNORECASE,
        )
        # 提取所有IP地址并去重
        ipv4_matches = ipv4_pattern.findall(text)
        ipv6_matches = ipv6_pattern.findall(text)
        all_ips = list(set(ipv4_matches + ipv6_matches))
        # 一次替换所有IP地址
        pattern = re.compile("|".join(re.escape(ip) for ip in all_ips))
        text = pattern.sub(self.special_token, text)

        data[self.content] = text
        return data

        # matches = re.findall(pattern, text, re.DOTALL)
        # for item in matches:
        #     text = re.sub(re.escape(item), self.special_token, text)
        # data[self.content] = text
        # return data
