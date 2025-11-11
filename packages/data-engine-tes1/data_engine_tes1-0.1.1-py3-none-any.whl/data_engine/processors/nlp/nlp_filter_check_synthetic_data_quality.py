from data_engine.core.base import BaseFilter, BaseTool
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class NlpFilterCheckSyntheticDataQuality(BaseFilter):
    """
    基于知识图谱的数据校验
    基于知识图谱对数据进行校验，确保数据的准确性和一致性：基于知识图谱的某一个由三元组组成的路径，检查对应的合成数据是否符路径表示的推理过程
    知识图谱合成行业数据专用算法
    """

    def __init__(self, similarity_threshold: float = 0.7, **kwargs):
        """
        初始化方法：
            similarity_threshold:文本相似度的阈值#用于判断两段文本是否相似，默认值为0.7。
        """
        only_ray = True
        super().__init__(**kwargs)
        self.similarity_threshold = similarity_threshold

    def process(self, data: dict):

        def extract_entities(text):
            # Extract entities enclosed in < >
            return set(re.findall(r"<([^>]+)>", text))

        def calculate_text_similarity(text1, text2):
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        text = str(data["question"] + data["answer"])
        evidence_str = data["evidence"]  # 假设evidence是一个字符串
        evidence_entities = extract_entities(evidence_str)
        synth_entities = extract_entities(text)

        # Calculate entity overlap ratio
        entity_overlap = len(evidence_entities.intersection(synth_entities)) / len(
            evidence_entities
        )

        # Calculate text similarity
        text_similarity = calculate_text_similarity(evidence_str, text)

        data["entity_overlap"] = entity_overlap
        data["text_similarity"] = text_similarity
        data["is_qualified_data"] = (
            entity_overlap >= 0.8 and text_similarity >= self.similarity_threshold
        )
        return data
