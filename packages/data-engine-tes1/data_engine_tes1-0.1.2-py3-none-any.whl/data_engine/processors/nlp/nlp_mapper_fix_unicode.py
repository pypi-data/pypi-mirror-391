from data_engine.core.base import BaseMapper
import ftfy
from typing import Optional, Dict, Any


class NlpMapperFixUnicode(BaseMapper):
    """
    损坏unicode修复
    用于修复文本中的 Unicode 编码错误，并可选地对文本进行标准化处理。该映射器基于 ftfy 库实现，适用于清洗存在乱码或非规范字符的自然语言文本数据。
    """

    SUPPORTED_NORMALIZATIONS = {"NFC", "NFKC", "NFD", "NFKD"}

    def __init__(
        self, normalization: Optional[str] = None, content: str = "text", **kwargs: Any
    ):
        """
        初始化方法
        normalization: 归一化方式#['NFC', 'NFKC', 'NFD', 'NFKD', None]#用于指定文本修复后的 Unicode 标准化方式，若为 None 则默认使用 'NFC' 格式
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.normalization = (normalization or "NFC").upper()
        self.content = content

        if self.normalization not in self.SUPPORTED_NORMALIZATIONS:
            raise ValueError(
                f"Unsupported normalization mode: '{self.normalization}'. "
                f"Must be one of {sorted(self.SUPPORTED_NORMALIZATIONS)}."
            )

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data[self.content] = ftfy.fix_text(
            data[self.content], normalization=self.normalization
        )
        return data
