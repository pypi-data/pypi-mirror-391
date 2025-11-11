from sklearn.manifold import TSNE
from data_engine.core.base import BaseFilter, BaseTool
import re
import ray
from tqdm import tqdm
import pandas as pd
from sentence_transformers import SentenceTransformer
from data_engine.utils.model_utils import get_model_path


class NlpFilterSemanticMapping(BaseTool):
    """
    指令数据集语义映射
    通过embedding模型获取数据集的向量表征，并利用t-sne算法进行降维
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, **kwargs):
        """
        初始化方法：
            model_name_or_path: 大模型的名字或路径#用于加载模型
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.llm_model = None

    def run(self, data):
        if not self.llm_model:
            self.llm_model = SentenceTransformer(self.model_name_or_path)
        data = data.to_pandas()
        data = data.to_dict(orient="records")
        conversations_reformat_sample = []
        array = []
        for item in data:
            conversation_txt = " ".join([j["content"] for j in item["content"]])
            conversations_reformat_sample.append(conversation_txt)
            array.append(item)
        conversation_repre_vectors = self.llm_model.encode(
            conversations_reformat_sample
        )
        NUM = conversation_repre_vectors.shape[0]
        tsne = TSNE(n_jobs=-1)
        perplexity = min(30, NUM - 1 if NUM > 1 else 1)
        tsne = TSNE(n_jobs=-1, perplexity=perplexity)
        X_tsne = tsne.fit_transform(conversation_repre_vectors)
        enhanced_data = []
        for i, conversation in enumerate(array):
            conversation["tsne_x"] = float(X_tsne[i, 0])
            conversation["tsne_y"] = float(X_tsne[i, 1])
            enhanced_data.append(conversation)
        import pyarrow as pa

        table = pa.Table.from_pylist(enhanced_data)
        return ray.data.from_arrow(table)
