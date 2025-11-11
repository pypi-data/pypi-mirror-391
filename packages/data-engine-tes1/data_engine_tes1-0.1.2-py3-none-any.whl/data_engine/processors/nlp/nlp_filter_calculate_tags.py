import math
from data_engine.core.base import BaseFilter


class NlpFilterCalculateTags(BaseFilter):
    """
    指令数据标签特征统计
    通过统计标签数量衡量指令数据集的多样性。
    后训练数据合成专用算法
    """

    only_ray = True

    def __init__(self, **kwargs):
        """
        初始化方法：
        """
        super().__init__(**kwargs)

    def process(self, data: dict):
        tags_num = len(data["tags"])
        data["calculate_tags"] = math.log(tags_num)
        return data
