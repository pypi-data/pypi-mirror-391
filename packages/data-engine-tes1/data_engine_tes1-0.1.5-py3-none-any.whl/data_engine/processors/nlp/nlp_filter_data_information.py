import os
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.stats import entropy
from tqdm import tqdm
import random
import pandas as pd
import os
import pickle
import pdb
import copy
import sys
import ray

from data_engine.core.base import BaseFilter, BaseTool


class NlpFilterDataInformation(BaseTool):
    """
    基于信息量的指令数据筛选
    据指令的信息量进行筛选，可以去除冗余、低质量或无关紧要的指令，从而优化数据集，提升模型的训练效果和泛化能力。
    后训练数据合成专用算法
    """

    only_ray = True

    def __init__(self, **kwargs):
        """
        初始化方法：
        """
        super().__init__(**kwargs)

    def _find_bins_2d(self, points, grid_size=10):
        """
        根据二维点的坐标，确定每个点所在的二维 bin，并返回一个存储每个 bin 包含的点索引的列表。

        参数:
        points : numpy.ndarray, 形状为 (N, 2)，表示 N 个二维点
        xedges : numpy.ndarray, X 轴的 bin 边界
        yedges : numpy.ndarray, Y 轴的 bin 边界

        返回:
        result : list of lists, 每个列表对应一个 bin，存储的是该 bin 中点的索引
        """
        x_coords = points[:, 0]
        y_coords = points[:, 1]

        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)

        histogram, x_edges, y_edges = np.histogram2d(
            x_coords, y_coords, bins=grid_size, range=[[x_min, x_max], [y_min, y_max]]
        )

        num_points = points.shape[0]

        x_bin_indices = np.digitize(points[:, 0], x_edges) - 1
        y_bin_indices = np.digitize(points[:, 1], y_edges) - 1

        num_x_bins = len(x_edges) - 1
        num_y_bins = len(y_edges) - 1

        result = [[[] for _ in range(num_y_bins)] for _ in range(num_x_bins)]

        for i in range(num_points):
            x_idx = x_bin_indices[i]
            y_idx = y_bin_indices[i]

            if 0 <= x_idx < num_x_bins and 0 <= y_idx < num_y_bins:
                result[x_idx][y_idx].append(i)

        return result

    def run(self, data):
        data = data.to_pandas()
        data = data.to_dict(orient="records")
        data_tsne = np.array([[item["tsne_x"], item["tsne_y"]] for item in data])
        loss_ls = np.array([sample["loss"] for sample in data])
        GRID_SIZE = 400
        SMOOTH_DIAGRAM = 1
        bin_sample_ls = self._find_bins_2d(data_tsne, GRID_SIZE)
        loss_thre = np.quantile(loss_ls, [0.3])
        thre = loss_thre[0]
        sample_id_ls_tmp = []
        for ith, i in enumerate(bin_sample_ls):
            for jth, j in enumerate(i):
                if len(loss_ls[j]) > 0:
                    sample_id_ls_tmp.extend(np.array(j)[loss_ls[j] < thre].tolist())
        sample_ls_tmp = [data[i] for i in sample_id_ls_tmp if isinstance(i, int)]
        import pyarrow as pa

        table = pa.Table.from_pylist(sample_ls_tmp)
        return ray.data.from_arrow(table)
