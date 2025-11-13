from data_engine.core.base import BaseMapper


class NlpMapperWhitespaceNormalizer(BaseMapper):
    """
    空白字符归一化映射器
    该类用于将文本中出现的多种空白字符统一归一为标准 ASCII 空格字符 ' '，以提升文本处理的一致性。
    通常用于文本清洗的预处理阶段，尤其在多语言或多平台数据中可能存在各种不可见的空白符号。
    """

    def __init__(self, content: str = "text", **kwargs):
        """
        初始化方法：
            content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.content = content

    def process(self, data: dict) -> dict:
        VARIOUS_WHITESPACES = {
            "\u0009",  # CHARACTER TABULATION
            "\u000a",  # LINE FEED
            "\u000b",  # LINE TABULATION
            "\u000c",  # FORM FEED
            "\u000d",  # CARRIAGE RETURN
            "\u0020",  # SPACE
            "\u0085",  # NEXT LINE
            "\u00a0",  # NO-BREAK SPACE
            "\u1680",  # OGHAM SPACE MARK
            "\u180e",  # MONGOLIAN VOWEL SEPARATOR (deprecated but still used)
            "\u2000",  # EN QUAD
            "\u2001",  # EM QUAD
            "\u2002",  # EN SPACE
            "\u2003",  # EM SPACE
            "\u2004",  # THREE-PER-EM SPACE
            "\u2005",  # FOUR-PER-EM SPACE
            "\u2006",  # SIX-PER-EM SPACE
            "\u2007",  # FIGURE SPACE
            "\u2008",  # PUNCTUATION SPACE
            "\u2009",  # THIN SPACE
            "\u200a",  # HAIR SPACE
            "\u2028",  # LINE SEPARATOR
            "\u2029",  # PARAGRAPH SEPARATOR
            "\u202f",  # NARROW NO-BREAK SPACE
            "\u205f",  # MEDIUM MATHEMATICAL SPACE
            "\u3000",  # IDEOGRAPHIC SPACE
            "\ufeff",  # ZERO WIDTH NO-BREAK SPACE (deprecated)
        }

        text = data[self.content].strip()
        normalized_text = "".join(
            char if char not in VARIOUS_WHITESPACES else " " for char in text
        )
        data[self.content] = normalized_text
        return data
