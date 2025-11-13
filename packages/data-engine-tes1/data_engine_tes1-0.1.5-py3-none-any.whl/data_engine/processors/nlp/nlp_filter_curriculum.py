import os
import json
import os
import random
import pdb
from data_engine.core.base import BaseFilter, BaseTool
import ray
import pandas as pd


class NlpFilterCurriculum(BaseTool):
    """
    基于课程学习的指令数据选择与优化
    通过分析不同类型指令数据集的能力依赖关系，调整数据集的学习顺序。
    后训练数据合成专用算法
    """

    only_ray = True

    def __init__(self, **kwargs):
        """
        初始化方法：
        """
        super().__init__(**kwargs)

    def _get_tag_ls(self, sample_ls):
        sample_id_dict = {}
        for i, sample in enumerate(sample_ls):
            tag = random.choice(sample["tags_label"])
            try:
                sample_id_dict[tag]
            except:
                sample_id_dict[tag] = []
            sample_id_dict[tag].append(sample)
        return sample_id_dict

    def run(self, data):
        data = data.to_pandas()
        data = data.to_dict(orient="records")
        array = []
        for item in data:
            if len(item["tags_label"]) == 0:
                continue
            array.append(item)
        data = array
        # data = [item for item in data if item["tags_label"]]
        NUM = len(data)
        random.shuffle(data)
        sample_dict = self._get_tag_ls(data)
        base_cate = [
            "javascript编程",
            "java编程",
            "python编程",
            "数学建模",
            "数学推理",
            "数学计算",
            "算法分析",
            "编程能力",
        ]
        dependent_cate = [
            "人文历史哲学与社会学知识",
            "人物理解",
            "任务生成",
            "信息提供",
            "创意与设计",
            "常识理解",
            "开放知识问答",
            "教育与咨询",
            "文学创作与艺术知识",
            "文本摘要",
            "信息组织",
            "沟通与社交媒体",
            "知识理解",
        ]
        dependent_cate_sample_ls = [
            s for k in dependent_cate if k in sample_dict for s in sample_dict[k]
        ]
        base_cate_sample_ls = [
            s for k in base_cate if k in sample_dict for s in sample_dict[k]
        ]
        middle_cate_sample_ls = [
            s
            for k in set(sample_dict.keys())
            .difference(dependent_cate)
            .difference(base_cate)
            for s in sample_dict[k]
        ]
        random.shuffle(base_cate_sample_ls)
        random.shuffle(dependent_cate_sample_ls)

        if NUM < 50000:
            proportion_num = 10
        else:
            proportion_num = 20
        sch_sample = (
            base_cate_sample_ls
            + base_cate_sample_ls[: int(len(data) / proportion_num)]
            + middle_cate_sample_ls
            + dependent_cate_sample_ls[: -int(len(data) / proportion_num)]
        )
        random.shuffle(sch_sample)
        sch_sample += random.sample(
            base_cate_sample_ls + middle_cate_sample_ls + dependent_cate_sample_ls, NUM
        )
        # sch_sample += random.sample(base_cate_sample_ls[int(len(data)/proportion_num):] + middle_cate_sample_ls + dependent_cate_sample_ls + dependent_cate_sample_ls[-int(len(data)/proportion_num):], NUM)
        import pyarrow as pa

        table = pa.Table.from_pylist(sch_sample)
        return ray.data.from_arrow(table)
