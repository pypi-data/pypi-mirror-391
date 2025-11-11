from data_engine.core.base import BaseFilter, BaseTool
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from typing import Dict, List, Set
import re
import ray
import json
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
from data_engine.utils.model_utils import get_model_path


class NlpFilterTagsNorm(BaseTool):
    """
    指令数据集标签归一化
    标签归一化是指将不同格式、不同表述的标签统一为一种标准化的形式。
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(
        self, model_name_or_path: str, top_n: int, similarity_threshold: float, **kwargs
    ):
        """
        初始化方法：
            model_name_or_path: 大模型的名字或路径#用于加载模型
            top_n: 取前n个#根据频率排序，取前n个高频词标签
            similarity_threshold: 相似度阈值#用于相似度判断
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.top_n = top_n
        self.similarity_threshold = similarity_threshold
        self.llm_model = None

    def _extract_and_count_tags(self, data: List[Dict]) -> Counter:

        all_tags = []
        for item in data:
            all_tags.extend(item["tags"])
        tag_counter = Counter(all_tags)
        print(f"总共发现 {len(tag_counter)} 个不同的标签")

        return tag_counter

    def _get_top_tags(self, tag_counter: Counter, top_n: int = 1000) -> List[str]:

        top_tags = [tag for tag, count in tag_counter.most_common(top_n)]
        print(f"提取前 {len(top_tags)} 个标签")
        return top_tags

    def _compute_tag_similarities(self, tags: List[str]) -> np.ndarray:
        if not tags:
            return np.array([])

        tag_embeddings = self.llm_model.encode(
            tags,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        if tag_embeddings.ndim == 1:
            tag_embeddings = tag_embeddings.reshape(1, -1)

        if tag_embeddings.shape[0] < 2:
            return np.eye(tag_embeddings.shape[0])  # 至少返回个对角矩阵

        similarity_matrix = cosine_similarity(tag_embeddings)
        return similarity_matrix

    def _merge_similar_tags_advanced(
        self, tags: List[str], similarity_matrix: np.ndarray
    ) -> Dict[str, List[str]]:

        n = len(tags)
        adj_list = {i: [] for i in range(n)}
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] >= self.similarity_threshold:
                    adj_list[i].append(j)
                    adj_list[j].append(i)

        visited = [False] * n
        components = []

        def dfs(node, component):
            visited[node] = True
            component.append(node)
            for neighbor in adj_list[node]:
                if not visited[neighbor]:
                    dfs(neighbor, component)

        for i in range(n):
            if not visited[i]:
                component = []
                dfs(i, component)
                components.append(component)

        synonym_dict = {}
        for component in components:
            main_tag = tags[min(component)]
            synonym_list = [tags[idx] for idx in component]
            synonym_dict[main_tag] = synonym_list

        return synonym_dict

    def run(self, data):
        data = data.to_pandas()
        data = data.to_dict(orient="records")

        if not self.llm_model:
            self.llm_model = SentenceTransformer(self.model_name_or_path)

        tag_counter = self._extract_and_count_tags(data)
        top_tags = self._get_top_tags(tag_counter, top_n=self.top_n)

        similarity_matrix = self._compute_tag_similarities(top_tags)
        synonym_dict = self._merge_similar_tags_advanced(top_tags, similarity_matrix)

        result_dict = {}
        for key, values in synonym_dict.items():
            for value in values:
                result_dict[value] = key
        array = []
        for line in data:
            if len(line["tags"]) == 0:
                continue
            line["tags_norm"] = list(
                set([result_dict[tag] for tag in line["tags"] if tag in result_dict])
            )
            array.append(line)

        import pyarrow as pa

        table = pa.Table.from_pylist(array)
        return ray.data.from_arrow(table)
