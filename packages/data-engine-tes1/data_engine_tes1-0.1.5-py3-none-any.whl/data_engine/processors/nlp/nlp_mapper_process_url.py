from data_engine.core.base import BaseFilter, BaseMapper
import re
from tqdm import tqdm


class NlpMapperProcessUrl(BaseMapper):
    """
    链接清理
    该算子是一种高效的文本处理工具，专门设计用于从大量文本数据中快速、准确地识别URL。
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
        # pattern = r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?"
        patterns = [
            r"(?:https?|ftp|mailto)://[^\s<>'\"]+",
            r"(?<!@)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,}|co\.uk|org\.cn|com\.cn|net\.cn|gov\.cn)(?:/[a-zA-Z0-9_.~!*'();:@&=+$,%#-]*)*(?:\?[a-zA-Z0-9_.~!*'():@&=+$,%#-]*)?(?:#[a-zA-Z0-9_.~!*'();:@&=+$,%#-]*)?",
        ]

        url_matches = []
        for pattern in patterns:
            # 使用re.UNICODE确保匹配正常
            matches = re.findall(pattern, text, re.UNICODE)
            url_matches.extend(matches)

        # 去重并按长度排序（长匹配优先，避免部分替换）
        unique_matches = sorted(
            list(set(url_matches)), key=lambda x: len(x), reverse=True
        )
        # print(f' matches ==333:{unique_matches}')

        for item in unique_matches:
            # print(f' item ==333{item}')
            text = re.sub(
                re.escape(item), self.special_token, text, flags=re.IGNORECASE
            )
        data[self.content] = text
        return data
