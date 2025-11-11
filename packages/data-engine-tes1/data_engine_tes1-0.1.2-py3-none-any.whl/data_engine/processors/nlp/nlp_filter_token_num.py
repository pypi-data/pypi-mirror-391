import sys
from data_engine.core.base import Base, BaseProcessor, BaseFilter
from data_engine.utils.model_utils import get_huggingface_model
from data_engine.utils.model_utils import get_model_path


class NlpFilterTokenNum(BaseFilter):
    """
    令牌数量过滤器
    用于过滤文本样本中总令牌数量不在指定范围内的样本。通过分析输入文本的令牌数量，判断是否保留样本。
    """

    only_ray = True

    def __init__(
        self,
        model_name_or_path: str = "Qwen2.5-0.5B",
        min_num: int = 10,
        max_num: int = None,
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        model_name_or_path: 模型路径#用于加载 Hugging Face 模型和分词器的模型路径。
        min_num: 最小令牌数量#样本保留的最小令牌数量阈值。
        max_num: 最大令牌数量#样本保留的最大令牌数量阈值。
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.min_num = min_num
        self.max_num = max_num or sys.maxsize
        self.model_path = get_model_path(model_name_or_path)
        self.tokenizer = None
        self.content = content

    def process(self, data):
        if self.tokenizer is None:
            result = get_huggingface_model(
                model_path=self.model_path,
                load_tokenizer=True,
                load_model=False,
                load_processor=False,
            )
            self.tokenizer = result["tokenizer"]

        token_num = len(self.tokenizer.encode(data[self.content]))
        data["token_num"] = token_num
        if self.do_filter:
            if token_num >= self.min_num and token_num <= self.max_num:
                return data
            else:
                return {}
        return data
