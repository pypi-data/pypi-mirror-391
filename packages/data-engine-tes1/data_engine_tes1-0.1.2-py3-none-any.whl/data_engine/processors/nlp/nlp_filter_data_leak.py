from data_engine.core.base import BaseFilter
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import json
import re
from tqdm import tqdm
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from data_engine.utils.model_utils import get_model_path


class NlpFilterDataLeak(BaseFilter):
    """
    指令数据集泄漏检测
    检测搜集指令数据集是否存在于评测数据集中，防止出现数据集泄露。
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, path: str = None, **kwargs):
        """
        初始化方法：
            model_name_or_path:大模型的名字或路径#用于加载模型
            path:数据集路径#用于加载待检评测测数据集路径
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.path = path
        self.llm_model = None
        self.embeddings_db = None
        self.data_base_dict = None

    def _load(self, filePath):
        with open(filePath) as f:
            data = [json.loads(item) for item in f]
            return data

    def _parserDataFromCsv(self, filePath):
        dataBaseDict = {}
        items = self._load(filePath)
        for index, item in enumerate(items):
            lineDict = {"index": 0, "query": None}
            lineDict["index"] = index
            try:
                lineDict["query"] = item["content"][0]["content"]
                lineDict["id"] = item["id"]
            except:
                print("Error: ", index, item)
            dataBaseDict[index] = lineDict
        return dataBaseDict

    def _init_embeddings_db(self, filePath):
        """初始化嵌入向量数据库"""
        dataBaseDict = self._parserDataFromCsv(filePath)
        queryList = list(
            map(lambda key: dataBaseDict[key]["query"], dataBaseDict.keys())
        )

        print("正在生成嵌入向量...")
        embeddings = self.llm_model.encode(queryList, show_progress_bar=True)
        embeddings = np.array(embeddings, dtype=np.float32)

        print(f"嵌入向量数据库初始化完成，总数目: {len(embeddings)}")
        return embeddings, dataBaseDict

    def _cosine_similarity_search(self, query_embedding, top_k=5):
        """
        使用余弦相似度进行向量搜索
        返回距离和索引
        """
        # 计算余弦相似度
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1), self.embeddings_db
        )[0]

        # 获取top_k个最相似的结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_similarities = similarities[top_indices]

        # 转换为距离（1 - 相似度）
        distances = 1 - top_similarities

        return distances, top_indices

    def _euclidean_distance_search(self, query_embedding, top_k=5):
        """
        使用欧几里得距离进行向量搜索
        返回距离和索引
        """
        # 计算欧几里得距离
        distances = np.linalg.norm(self.embeddings_db - query_embedding, axis=1)

        # 获取top_k个最近的结果
        top_indices = np.argsort(distances)[:top_k]
        top_distances = distances[top_indices]

        return top_distances, top_indices

    def _manhattan_distance_search(self, query_embedding, top_k=5):
        """
        使用曼哈顿距离进行向量搜索
        返回距离和索引
        """
        # 计算曼哈顿距离
        distances = np.sum(np.abs(self.embeddings_db - query_embedding), axis=1)

        # 获取top_k个最近的结果
        top_indices = np.argsort(distances)[:top_k]
        top_distances = distances[top_indices]

        return top_distances, top_indices

    def _vector_search(self, query_embedding, top_k=5, method="cosine"):
        """
        向量搜索主函数
        method: 'cosine', 'euclidean', 'manhattan'
        """
        if method == "cosine":
            return self._cosine_similarity_search(query_embedding, top_k)
        elif method == "euclidean":
            return self._euclidean_distance_search(query_embedding, top_k)
        elif method == "manhattan":
            return self._manhattan_distance_search(query_embedding, top_k)
        else:
            raise ValueError(f"Unsupported search method: {method}")

    def process(self, data):
        # 初始化模型
        if not self.llm_model:
            self.llm_model = SentenceTransformer(self.model_name_or_path)

        # 初始化嵌入向量数据库
        if self.embeddings_db is None:
            self.embeddings_db, self.data_base_dict = self._init_embeddings_db(
                self.path
            )

        # 获取查询文本
        text = data["content"][0]["content"]

        # 生成查询向量
        query_embedding = self.llm_model.encode([text])
        query_embedding = np.array(query_embedding[0], dtype=np.float32)

        # 进行向量搜索（使用余弦相似度，你也可以改为 'euclidean' 或 'manhattan'）
        distances, indices = self._vector_search(
            query_embedding, top_k=3, method="cosine"
        )

        # 判断是否数据泄露（注意：这里的阈值需要根据使用的距离方法调整）
        # 对于余弦距离，0.3是一个合理的阈值
        # 对于欧几里得距离，阈值可能需要更大
        if distances[0] < 0.3:
            data["data_leak"] = True
        else:
            data["data_leak"] = False

        return data
