import gzip
from data_engine.core.base import BaseFilter


class NlpFilterCompressibilityRatio(BaseFilter):
    """
    计算数据压缩比
    用于根据文本的压缩比（compressed size / original size）过滤样本。该过滤器利用 gzip 算法对输入文本进行压缩，
    计算压缩前后的字节长度比值。压缩比越小，表示文本信息密度越低（冗余度更高）。若压缩比小于设定的最小阈值，
    则该样本会被过滤。
    """

    def __init__(self, min_ratio: float = 0.5, content: str = "text", **kwargs):
        """
        初始化方法
        min_ratio: 最小压缩比 #[0,1]# 若文本压缩比（压缩后字节数/原始字节数）小于该值，则认为文本冗余度高，予以过滤
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.min_ratio = min_ratio
        self.content = content

    def process(self, data):
        text = data[self.content]
        encoded_text = text.encode("utf-8")
        original_size = len(encoded_text)
        if original_size == 0:
            return {}

        compressed_size = len(gzip.compress(encoded_text))
        compression_ratio = compressed_size / original_size
        data["compression_ratio"] = compression_ratio

        if self.do_filter and compression_ratio < self.min_ratio:
            return {}

        return data
