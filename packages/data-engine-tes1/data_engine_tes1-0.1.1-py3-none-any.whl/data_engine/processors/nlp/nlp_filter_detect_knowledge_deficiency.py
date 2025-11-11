import os
import sys
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))

# 将子目录添加到 sys.path
sys.path.append(current_dir)
from kg_rag.utility import *
from data_engine.core.base import BaseFilter, BaseTool
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer, AutoModelForCausalLM
from data_engine.utils.model_utils import get_model_path


class NlpFilterDetectKnowledgeDeficiency(BaseFilter):
    """
    基于知识图谱的大模型领域知识缺陷检测
    基于知识图谱检测大模型的领域知识缺陷，发现模型不足之处：从若干蒙特卡洛搜索树(MCTS)路径中，搜索出置信度最低的路径
    知识图谱合成行业数据专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(
        self,
        model_name_or_path: str,
        kg_file_path: str,
        temperature: float = 0.8,
        **kwargs
    ):
        """
        初始化方法：
            model_name_or_path:模型的名字或路径#用于加载模型
            kg_file_path:知识图谱文件路径#用于加载知识图谱
            temperature:温度#控制的是模型生成文本时的随机性或多样性
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.temperature = temperature
        self.kg_file_path = get_model_path(kg_file_path)
        self.llm_model = None
        self.tokenizer = None

    def process(self, data: dict):
        """
        参数：
            mcts_path_ls: MCTS路径的列表
        """
        set_seed(42)
        # 初始化KG：使用所有seed entity 构建一个总的KG; 之后对每一个seed entity使用MCTS进行搜索,用于合成数据
        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path,
                gpu_memory_utilization=0.8,
                tensor_parallel_size=1,
                enforce_eager=True,
            )

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
            self.kg = KnowledgeGraph(self.tokenizer, self.llm_model)

        kg_data = pd.read_csv(self.kg_file_path, dtype={"weight": float})

        self.kg.load_from_df(kg_data)
        self.kg_query = KGQuery(self.kg)
        self.alg_SE = StructEntropy(self.kg.graph)

        mcts = MCTS(self.llm_model, self.kg_query, self.alg_SE, num_simulations=100)

        node = data["root"]
        best_path = mcts.collect_paths_above_threshold(node)  # 搜索出置信度最低的路径

        data["root"] = best_path

        return data
