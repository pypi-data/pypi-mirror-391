from pydantic import Field
from typing import Literal
import torch
from data_engine.utils.model_utils import get_huggingface_model
from data_engine.core.base import BaseFilter
from data_engine.utils.model_utils import get_model_path


class NlpFilterQualityScore(BaseFilter):
    """
    文本质量
    用于根据模型预测的质量分数对文本进行过滤。其核心逻辑是通过加载指定模型计算文本的质量分数，并根据设定的最小阈值过滤低质量样本。
    """

    use_class = True

    def __init__(
        self,
        model_name_or_path: str = "quality_score",
        min_score: float = 2.0,
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        model_name_or_path: 模型路径#用于加载模型的路径
        min_score: 最小质量分数阈值#若文本的质量分数低于该值，则文本会被过滤
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.model_path = get_model_path(model_name_or_path)
        self.model = None
        self.min_score = min_score
        self.content = content

    def process(self, data):
        if self.model is None:
            result = get_huggingface_model(self.model_path, load_config=True)
            self.model, self.processor, self.config = (
                result["model"],
                result["processor"],
                result["config"],
            )
        inputs = self.processor(
            [data[self.content][:1024]],
            padding=True,
            truncation=True,
            max_length=1024,
            return_tensors="pt",
            add_special_tokens=True,
        ).to(self.model.device)
        values = self.model(**inputs, return_dict=True)

        predit_score = values.logits.tolist()[0][0]
        predit_score = float(predit_score)
        data["quality_score"] = predit_score
        if self.do_filter:
            return data if data["quality_score"] > self.min_score else {}
        return data
