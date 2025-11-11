from selectolax import parser
from data_engine.core.base import BaseMapper


class CleanHtmlMapper(BaseMapper):
    """
    HTML标签清理
    用于清理文本样本中的HTML代码，将特定HTML标签转换为文本格式，并去除其他HTML标签，提取纯文本内容。
    """

    def __init__(self, content: str = "text", **kwargs):
        """
        初始化方法：
            content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.content = content

    def process(self, data):
        text = data[self.content]
        text = text.replace("<li>", "\n*")
        text = text.replace("</li>", "")
        text = text.replace("<ol>", "\n*")
        text = text.replace("</ol>", "")
        result = parser.HTMLParser(text)
        data[self.content] = result.text()
        return data
