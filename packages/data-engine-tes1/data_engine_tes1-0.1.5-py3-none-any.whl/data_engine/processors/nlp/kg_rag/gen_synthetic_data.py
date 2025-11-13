import os
import pandas as pd
from kg_rag.utility import *


NODE_CONTEXT_PATH = config_data["NODE_CONTEXT_PATH"]

node_context_df = pd.read_csv(NODE_CONTEXT_PATH)


def reformat_sample(sample, evidences, value, file_path):
    # 假设sample是字符串，并且格式固定为 "Question: ... Answer: ..."
    try:
        # 提取问题和答案
        question_start = sample.find("Question: ") + len("Question: ")
        answer_start = sample.find("Answer: ") + len("Answer: ")

        # 获取问题和答案内容
        question = sample[question_start : sample.find("Answer: ")].strip()
        answer = sample[answer_start:].strip()

        # 构造字典
        sample_data = {
            "Question": question,
            "Answer": answer,
            "Evidence": ",".join(evidences),
            "Reward": round(value, 2),
        }

        return sample_data

    except Exception as e:
        print(f"Error parsing sample: {e}")


class ModelKnowledgeDector:
    def __init__(self, kg_file_path, save_path, model_path):
        self.kg_file_path = kg_file_path
        self.save_path = save_path
        self.model_path = model_path
        # Load LLM model
        llm = LLMModel(self.model_path)
        self.tokenizer = llm.tokenizer
        self.model = llm.model
        self.llm = llm
        self.kg = KnowledgeGraph(self.tokenizer, self.model)

        # Load knowledge graph and create query interface
        df = pd.read_csv(self.kg_file_path)
        head_entities = set()
        if "disease_name" in df.columns:
            head_entities.update(df["disease_name"].dropna())  # dropna() 用于去掉空值

        self.seed_ent_pool = list(head_entities)
        context_list = []

        for filename in os.listdir(self.save_path):
            file_path = os.path.join(self.save_path, filename)
            context_table = pd.read_csv(file_path)
            context_list.append(context_table)
        final_context = pd.concat(context_list, axis=0, ignore_index=True)
        # 去重
        kg_data = final_context.drop_duplicates()
        kg_data = kg_data[pd.notna(kg_data["edge_type"])]

        self.kg.load_from_df(kg_data)  # .head(200)
        self.kg_query = KGQuery(self.kg)
        self.alg_SE = StructEntropy(self.kg.graph)

    def detect_knowledge_edge(self):
        set_seed(42)
        # 初始化KG：使用所有seed entity 构建一个总的KG; 之后对每一个seed entity使用MCTS进行搜索,用于合成数据

        mcts = MCTS(self.model, self.kg_query, self.alg_SE, num_simulations=100)
        self.mcts_path_ls = []
        for seed_ent in tqdm(self.seed_ent_pool):
            try:
                _, mcts_path = mcts.search(seed_ent)
                self.mcts_path_ls.append(mcts_path)
            except:
                print("Entity Node not in KG")
                continue

        return self.mcts_path_ls

    def detect_knowledge_deficiency(self):
        best_path_ls = []
        for root in self.mcts_path_ls:
            best_path = root.search_best_path()
            best_path_ls.append(best_path)

        self.best_path_ls = best_path_ls
        return self.best_path_ls

    def generate_synthetic_data(self):
        set_seed(42)
        sample_ls = []
        for path in self.mcts_path_ls:
            evidences = []
            path_value = 0
            for node in path[1:]:
                node_value = node.value / (node.visits + 1)
                path_value += node_value
                sub = node.parent.state
                rel, obj = node.action
                ans = obj
                sub = "<" + sub + ">"
                obj = "<" + obj + ">"
                prompt = rel.format(sub)
                case = prompt + " " + obj
                evidences.append(case)

            evidences_str = "\n".join(evidences)
            # single
            sample = self.llm.gen_synthetic_data(evidences_str)
            sample_ls.append(reformat_sample(sample, evidences, path_value))

        print("Synthetic Dataset Generated Done!")
        return sample_ls
