from data_engine.core.base import BaseTool
import os, hashlib, nltk
from nltk.downloader import Downloader

Downloader().update_index = lambda *args, **kwargs: None
nltk.download = lambda *args, **kwargs: None
from unstructured.partition.auto import partition
from typing import List


def is_valid_file_type(path, file_type):
    """
    检查文件名称是否符合指定的文件类型
    参数:
        path : 文件路径
        file_type: 期望的文件类型（带点前缀，如 '.ppt'）

    返回:
        bool: 路径有效且符合文件类型返回True，否则返回False
    """
    # 提取文件扩展名并比较
    ext = os.path.splitext(path.lower())[1]
    return ext == file_type.lower()


class ToolExtract(BaseTool):
    """
    文本内容提取
    从doc docx eml pdf xml html ppt epub pptx xlsx 文件中提取文本内容，算子会自动推测文件格式。如果已知文件格式，建议使用更具体的算法处理，效率和准确性更高
    """

    only_ray = True

    def __init__(
        self,
        file_type: List[str] = [
            "doc",
            "docx",
            "eml",
            "pdf",
            "xml",
            "html",
            "ppt",
            "epub",
            "pptx",
            "xlsx",
        ],
        **kwargs,
    ):
        """
        初始化方法。
        file_type: 文件类型#文本内容提取支持的文件类型：doc,docx,eml,pdf,xml,html,ppt,epub,pptx,xlsx
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not data["path"].lower() not in self.file_type:
            return {}
        result = ""
        elements = partition(filename=data["path"], strategy="fast")
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractDoc(BaseTool):
    """
    doc文件中提取文本内容
    从doc文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".doc",
        **kwargs,
    ):
        """
        file_type: 文件类型#doc文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):

        # 先检查路径是否为空，再检查扩展名是否为.doc
        if not is_valid_file_type(data["path"], self.file_type):
            return {}

        from unstructured.partition.doc import partition_doc

        elements = partition_doc(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractDocx(BaseTool):
    """
    docx文件中提取文本内容
    从docx文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".docx",
        **kwargs,
    ):
        """
        file_type: 文件类型#docx文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.doc import partition_docx

        elements = partition_docx(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractEmail(BaseTool):
    """
    email文件中提取文本内容
    从email文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".eml",
        **kwargs,
    ):
        """
        file_type: 文件类型#email文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.email import partition_email

        elements = partition_email(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractEpub(BaseTool):
    """
    epub文件中提取文本内容
    从epub文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".epub",
        **kwargs,
    ):
        """
        file_type: 文件类型#epub文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.epub import partition_epub

        elements = partition_epub(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractHtml(BaseTool):
    """
    html文件中提取文本内容
    从html文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".html",
        **kwargs,
    ):
        """
        file_type: 文件类型#html文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.html import partition_html

        elements = partition_html(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractPdf(BaseTool):
    """
    pdf文件中提取文本内容
    从pdf文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".pdf",
        **kwargs,
    ):
        """
        file_type: 文件类型#pdf文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.pdf import partition_pdf

        elements = partition_pdf(filename=data["path"], strategy="fast")
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractPpt(BaseTool):
    """
    ppt文件中提取文本内容
    从ppt文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".ppt",
        **kwargs,
    ):
        """
        file_type: 文件类型#ppt文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        # 先检查路径是否为空，再检查扩展名是否为.ppt
        if not is_valid_file_type(data["path"], self.file_type):
            return {}

        from unstructured.partition.ppt import partition_ppt

        elements = partition_ppt(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractPptx(BaseTool):
    """
    pptx文件中提取文本内容
    从pptx文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".pptx",
        **kwargs,
    ):
        """
        file_type: 文件类型#pptx文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.ppt import partition_pptx

        elements = partition_pptx(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractXml(BaseTool):
    """
    xml文件中提取文本内容
    从xml文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".xml",
        **kwargs,
    ):
        """
        file_type: 文件类型#xml文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.xml import partition_xml

        elements = partition_xml(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data


class ToolExtractXlsx(BaseTool):
    """
    xlsx文件中提取文本内容
    从xlsx文件中提取文本内容
    """

    only_ray = True

    def __init__(
        self,
        file_type: str = ".xlsx",
        **kwargs,
    ):
        """
        file_type: 文件类型#doc文件
        """
        super().__init__(**kwargs)
        self.file_type = file_type

    def process(self, data: dict):
        if not is_valid_file_type(data["path"], self.file_type):
            return {}
        from unstructured.partition.xlsx import partition_xlsx

        elements = partition_xlsx(filename=data["path"])
        result = "\n".join([i.text for i in elements])
        data["text"] = result
        return data
