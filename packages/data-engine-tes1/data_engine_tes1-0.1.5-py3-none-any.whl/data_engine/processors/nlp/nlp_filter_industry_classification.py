from pydantic import Field
from typing import Literal
import torch
from data_engine.utils.model_utils import get_huggingface_model
from data_engine.core.base import BaseFilter
from data_engine.utils.model_utils import get_model_path


class NlpFilterIndustryClassification(BaseFilter):
    """
    行业分类标签
    用于对文本进行行业分类预测，并可选地根据指定行业进行样本过滤。该类基于 HuggingFace 兼容模型加载与推理实现，适用于需要行业标签赋值或按行业筛选的场景。
    支持延迟加载模型，仅在首次调用 `process` 方法时加载模型与处理器。
    """

    use_class = True

    def __init__(
        self,
        industry_type: str = None,
        model_name_or_path: str = "classification",
        content: str = "text",
        **kwargs
    ):
        """
        初始化方法
        model_name_or_path: 模型路径#用于加载 HuggingFace 格式的行业分类模型
        industry_type: 目标行业类型#仅保留行业类型匹配该值的样本
        content:文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.model_path = get_model_path(model_name_or_path)
        self.model = None
        self.industry_type = industry_type
        self.content = content

    def process(self, data):
        if self.model is None:
            result = get_huggingface_model(self.model_path, load_config=True)
            self.model, self.processor, self.config = (
                result["model"],
                result["processor"],
                result["config"],
            )
        id2label = self.config.id2label
        inputs = self.processor(
            [data[self.content][:1024]],
            padding=True,
            truncation=True,
            max_length=1024,
            return_tensors="pt",
            add_special_tokens=True,
        ).to(self.model.device)
        values = self.model(**inputs, return_dict=True)

        predict_label_scores = torch.argmax(values.logits, dim=-1).tolist()
        data["industry_type"] = id2label[predict_label_scores[0]]
        if self.do_filter and self.industry_type:
            return data if data["industry_type"] == self.industry_type else {}
        return data
