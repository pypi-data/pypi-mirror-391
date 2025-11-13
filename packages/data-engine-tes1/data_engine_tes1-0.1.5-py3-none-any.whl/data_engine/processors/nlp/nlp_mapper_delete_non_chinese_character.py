import regex as re
from data_engine.core.base import BaseMapper


class NlpMapperRemoveNonChineseCharacters(BaseMapper):
    """
    非中文字符移除算子
    用于文本预处理，移除文本中非中文字符，可选保留英文字母、数字以及中英文标点符号。
    """

    def __init__(
        self,
        keep_alphabet: bool = True,
        keep_number: bool = True,
        keep_punc: bool = True,
        content: str = "text",
        **kwargs,
    ):
        """
        初始化方法
        keep_alphabet: 是否保留英文字母#若为 True，则保留 A-Z、a-z 范围内的字母；否则移除
        keep_number: 是否保留数字#若为 True，则保留 0-9 的数字；否则移除
        keep_punc: 是否保留中英文标点#若为 True，则保留常见的中英文标点符号；否则移除
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)

        allowed_ranges = ["\u4e00-\u9fa5"]  # 中文字符范围

        if keep_alphabet:
            allowed_ranges.append("A-Za-z")
        if keep_number:
            allowed_ranges.append("0-9")
        if keep_punc:
            # 常见中英文标点符号
            punctuation = r'。，,、\-。%《》*/•&＆()（）—+：:？?!！“”""‘’\'；;·'
            allowed_ranges.append(re.escape(punctuation))  # 使用 re.escape 转义符号

        # 构建正则表达式：匹配所有不在允许字符范围内的字符
        allowed_char_group = "".join(allowed_ranges)
        self._pattern = f"[^{allowed_char_group}]"
        self.content = content

    def process(self, data: dict) -> dict:
        """
        处理单条文本样本，移除不符合规则的字符。

        :param data: 输入字典，需包含字段
        :return: 处理后的字典，文本已清洗
        """
        text = data[self.content]
        cleaned_text = re.sub(self._pattern, "", text, flags=re.DOTALL)
        data[self.content] = cleaned_text
        return data
