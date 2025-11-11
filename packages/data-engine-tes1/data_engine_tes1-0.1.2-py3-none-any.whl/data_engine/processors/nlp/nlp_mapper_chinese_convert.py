from data_engine.core.base import BaseMapper
import opencc
from functools import lru_cache


@lru_cache(maxsize=16)
def get_converter(mode: str):
    return opencc.OpenCC(f"{mode}.json")


class NlpMapperChineseConvert(BaseMapper):
    """
    繁体中文转换
    使用 OpenCC 实现繁体中文、简体中文和日文汉字的相互转换。
    支持多种预定义的转换模式，用于文本的语言风格标准化和格式调整。
    """

    _supported_modes = {
        "s2t",
        "t2s",
        "s2tw",
        "tw2s",
        "s2hk",
        "hk2s",
        "s2twp",
        "tw2sp",
        "t2tw",
        "tw2t",
        "hk2t",
        "t2hk",
        "t2jp",
        "jp2t",
    }

    def __init__(self, mode: str = "s2t", content: str = "text", **kwargs):
        """
        初始化方法
        mode: 转换模式#['s2t', 't2s', 's2tw', 'tw2s', 's2hk', 'hk2s', 's2twp', 'tw2sp','t2tw', 'tw2t', 'hk2t', 't2hk', 't2jp', 'jp2t']#OpenCC 提供的语言转换模式。
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)

        if mode not in self._supported_modes:
            raise ValueError(
                f"Unsupported mode '{mode}'. Supported modes: {sorted(self._supported_modes)}"
            )

        self.mode = mode
        self.content = content

    def process(self, data) -> dict:
        """
        Process a single data sample.

        :param data: dict with key 'text'
        :return: dict with converted 'text'
        """
        if not isinstance(data, dict) or "text" not in data:
            raise ValueError("Input must be a dict containing a 'text' field.")
        self.converter = get_converter(self.mode)
        text = data[self.content]

        data[self.content] = self.converter.convert(text)
        return data
