from .config import sim1, sim2, default_gemma, default_gemma_p
import json
import numpy as np
from tqdm import trange


def sim1(h1, h2):
    return np.dot(h1, h2)


def sim2(t1, t2):
    return t1 == t2


def read_jsonl(filename):
    with open(filename, encoding="utf8") as f:
        datas = f.readlines()
    datas_tmp = []
    for data in datas:
        data = json.loads(data)
        datas_tmp.append(data)
    return datas_tmp


def getrightwrong(datas, gemma_p, text_simfunc, alpha, beta, print_ave):
    right, wrong = [], []
    gemma_p_ave, text_sim_ave, negative_num = 0, 0, 0
    for data in datas:
        sim_value = text_simfunc(data["gold"], data["pred"])
        text_sim_ave += sim_value
        if sim_value > beta:
            right.append(data)
        elif sim_value < alpha:
            gemma_p_ave += data["gold_score"]
            negative_num += 1
            if data["gold_score"] < gemma_p:
                wrong.append(data)

    if print_ave:
        print(
            "average relative loglikelihood probability of negative example: {}".format(
                gemma_p_ave / negative_num
            )
        )
        print(
            "average similarity between predicted answer and gold answer: {}".format(
                text_sim_ave / len(datas)
            )
        )
        print(len(wrong))
    return right, wrong


class CEPEngine:
    def __init__(self, data, h_simfunc=sim1, text_simfunc=sim2):
        self.datas = data
        self.h_simfunc = h_simfunc
        self.text_simfunc = text_simfunc

    def extract(self, alpha=0.5, beta=0.5, gemma=0.6, gemma_p=0.82, print_ave=False):

        assert beta >= alpha
        negas = set()
        right_datas, wrong_datas = getrightwrong(
            self.datas, gemma_p, self.text_simfunc, alpha, beta, print_ave
        )
        data_pairs = []
        gemma_ave, gemma_num = 0, 0
        for i in trange(len(right_datas)):
            right_data = right_datas[i]
            v1 = np.array(right_data["representations"])
            for j, wrong_data in enumerate(wrong_datas):
                if (
                    self.text_simfunc(right_data["pred"], wrong_data["pred"]) > beta
                    and self.text_simfunc(right_data["gold"], wrong_data["gold"])
                    < alpha
                ):
                    v2 = np.array(wrong_data["representations"])
                    sim = self.h_simfunc(v1, v2)
                    gemma_ave += sim
                    gemma_num += 1
                    if sim > gemma:
                        data_pairs.append((i, j))
                        negas.add(j)

        return data_pairs
