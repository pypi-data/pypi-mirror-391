from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import json
from sklearn.cluster import DBSCAN
import numpy as np
from .config import default_eps, default_min_examples
from tqdm import tqdm
import os


def readjsonl(filename):
    with open(filename, encoding="utf8") as f:
        datas = f.readlines()
    datas_tmp = []
    for data in datas:
        data = json.loads(data)
        datas_tmp.append(data)
    return datas_tmp


class ClusterEngine:
    def __init__(self, cep_pairs, orig_datas):
        self.cep_pairs = cep_pairs
        self.orig_datas = orig_datas

    def cluster(
        self, eps=None, min_examples=None, ratio=0.04, n_components=2, alpha=0.08
    ):

        datas, negas, posis = [], [], []
        num = 0.0
        # for i in tqdm(range(len( self.orig_datas))):
        for i in tqdm(range(10000)):
            posi_data = self.orig_datas[self.cep_pairs[i][0]]
            nega_data = self.orig_datas[self.cep_pairs[i][1]]
            result = []
            for j in range(len(posi_data["representations"])):
                if (
                    posi_data["representations"][j] + nega_data["representations"][j]
                ) == 0 or abs(
                    posi_data["representations"][j] - nega_data["representations"][j]
                ) / (
                    posi_data["representations"][j] + nega_data["representations"][j]
                ) < ratio:
                    result.append(
                        (
                            posi_data["representations"][j]
                            + nega_data["representations"][j]
                        )
                        / 2
                    )
                    num += 1
                else:
                    result.append(0)
            datas.append(result)
            posis.append((posi_data["content"], posi_data["gold"], posi_data["pred"]))
            negas.append((nega_data["content"], nega_data["gold"], nega_data["pred"]))

        datas = np.array(datas)
        pca_tool = PCA()
        pca = pca_tool.fit_transform(datas)[:, :n_components]
        del pca_tool
        del datas
        y_pred = DBSCAN(eps=eps, min_samples=min_examples).fit_predict(pca)
        notinanycluster_num = 0
        d = []
        results, results_neg = {}, {}
        for i in range(10000):
            if i in y_pred:
                d.append(i)
                results[i] = []
                results_neg[i] = set()
            else:
                break

        pca1, pca2, y_pred1 = [], [], []
        for i in range(len(y_pred)):
            if y_pred[i] != -1:
                results[y_pred[i]].append((posis[i], negas[i]))
                results_neg[y_pred[i]].add(negas[i])
                pca1.append(pca[i][0])
                pca2.append(pca[i][1])
                y_pred1.append(y_pred[i])
            else:
                notinanycluster_num += 1

        for key in results_neg:
            results_neg[key] = list(results_neg[key])
        print("number of cluster categories:", len(d))

        return results
