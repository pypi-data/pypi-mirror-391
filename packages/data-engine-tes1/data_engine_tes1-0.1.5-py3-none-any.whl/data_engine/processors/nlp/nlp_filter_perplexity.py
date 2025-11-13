import sys
import torch
from data_engine.core.base import BaseFilter
from data_engine.utils.model_utils import get_huggingface_model, get_model_path


class NlpFilterPerplexity(BaseFilter):
    """
    困惑度
    用于基于语言模型的困惑度（Perplexity）对样本进行过滤。通过计算输入文本的困惑度值，将超过设定阈值的样本过滤掉。
    """

    use_class = True

    def __init__(
        self,
        model_name_or_path: str,
        max_ppl: int = 1000,
        content: str = "text",
        *args,
        **kwargs
    ):
        """
        初始化方法
        model_name_or_path: 模型路径 #指定用于计算困惑度的预训练语言模型的路径
        max_ppl: 最大困惑度阈值 #样本困惑度值不得超过此值，超过的样本将被过滤
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(*args, **kwargs)
        self.model = None
        self.processor = None
        self.model_path = get_model_path(model_name_or_path)
        self.max_ppl = max_ppl
        self.content = content

    def process(self, data: dict) -> dict:
        if self.model is None:
            result = get_huggingface_model(model_path=self.model_path)
            self.model, self.processor = result["model"], result["processor"]

        inputs = self.processor(
            [data[self.content]],
            padding=True,
            truncation=True,
            max_length=1024,
            return_tensors="pt",
            add_special_tokens=True,
        ).to(self.model.device)
        outputs = self.model(**inputs, labels=inputs["input_ids"])
        data["perplexity"] = torch.exp(outputs.loss).item()

        if self.do_filter:
            return data if data["perplexity"] <= self.max_ppl else {}
        return data
