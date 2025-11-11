import os
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.stats import entropy
from tqdm import tqdm
import random
import os
import pickle
import pdb
import copy
import sys
from data_engine.core.base import BaseFilter, BaseTool
import ray
import pandas as pd


class NlpFilterDataDiversity(BaseTool):
    """
    基于多样性的指令数据筛选
    根据指令多样性筛选数据，确保指令数据覆盖广泛场景
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

        # Get the min and max for each axis
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)

        # Create a 2D histogram (grid)
        histogram, x_edges, y_edges = np.histogram2d(
            x_coords, y_coords, bins=grid_size, range=[[x_min, x_max], [y_min, y_max]]
        )

        # 获取点的数量
        num_points = points.shape[0]

        # 使用 np.digitize 确定每个点在 x 和 y 方向上分别落在哪个 bin 内
        x_bin_indices = np.digitize(points[:, 0], x_edges) - 1  # 对 X 轴进行 bin 分配
        y_bin_indices = np.digitize(points[:, 1], y_edges) - 1  # 对 Y 轴进行 bin 分配

        # 创建一个二维列表，存储每个 bin 中的点索引
        num_x_bins = len(x_edges) - 1  # X 方向的 bin 数量
        num_y_bins = len(y_edges) - 1  # Y 方向的 bin 数量

        result = [[[] for _ in range(num_y_bins)] for _ in range(num_x_bins)]

        # 遍历每个点，将其索引放入对应的 bin 中
        for i in range(num_points):
            x_idx = x_bin_indices[i]
            y_idx = y_bin_indices[i]

            # 检查 x_idx 和 y_idx 是否在有效的 bin 范围内
            if 0 <= x_idx < num_x_bins and 0 <= y_idx < num_y_bins:
                result[x_idx][y_idx].append(i)

        return result

    def _count_smooth(self, histogram, n):

        original_histogram = histogram.copy()

        rows, cols = histogram.shape

        for i in tqdm(range(rows)):
            for j in range(cols):
                if histogram[i, j] == 0:
                    min_neighbor = float("inf")

                    for di in range(-n, n + 1):
                        for dj in range(-n, n + 1):

                            if abs(di) + abs(dj) <= n:
                                ni, nj = i + di, j + dj
                                if 0 <= ni < rows and 0 <= nj < cols:
                                    neighbor_value = original_histogram[ni, nj]
                                    if neighbor_value > 0:
                                        min_neighbor = min(min_neighbor, neighbor_value)

                    if min_neighbor != float("inf"):
                        histogram[i, j] = max(1, np.floor(min_neighbor * 0.5))

        return histogram

    def _calculate_spatial_entropy(
        self,
        points,
        grid_size=10,
        smooth_diagram=5,
        smooth=False,
        zero_bin_ls=[],
        filter_thre=None,
        weights=None,
    ):

        x_coords = points[:, 0]
        y_coords = points[:, 1]

        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)

        histogram, x_edges, y_edges = np.histogram2d(
            x_coords, y_coords, bins=grid_size, range=[[x_min, x_max], [y_min, y_max]]
        )

        if smooth:
            histogram = self._count_smooth(histogram, smooth_diagram)

        for zero_cord in zero_bin_ls:
            histogram[zero_cord[0], zero_cord[1]] = 0.1

        if filter_thre:
            bin_sample_ls = self._find_bins_2d(points, grid_size)
            weights = np.array(weights)
            for ith, i in enumerate(bin_sample_ls):
                for jth, j in enumerate(i):
                    if len(weights[j]) > 0:
                        if max(weights[j]) < filter_thre:
                            histogram[ith][jth] = 0.1
                        else:
                            histogram[ith][jth] = sum(weights[j] < filter_thre)

        original_histogram = histogram.copy()

        probabilities = histogram.flatten() / np.sum(histogram)

        probabilities = probabilities[probabilities > 0]

        spatial_entropy = entropy(probabilities)

        return spatial_entropy

    def _entropy_filter(self, entropy_ls):
        for i in range(1, len(entropy_ls)):
            if entropy_ls[i] > entropy_ls[i - 1]:
                entropy_ls[i] = entropy_ls[i - 1] - 0.01

        return entropy_ls

    def _cal_cut_thre(self, num_ls, quantiles, num_region=100):
        low = min(num_ls)
        up = max(num_ls)
        piece_size = (up - low) / num_region
        return [low + q * piece_size for q in quantiles]

    def _find_edge_ids(self, entropy_ls, cut_thre):

        bin_indices = np.digitize(entropy_ls, cut_thre) - 1

        result = [[] for _ in range(len(cut_thre) - 1)]

        for i, bin_idx in enumerate(bin_indices):
            if 0 <= bin_idx < len(result):
                result[bin_idx].append(i)

        thre_ids = [i[-1] for i in result]

        return thre_ids

    def run(self, data):

        data = data.to_pandas()
        data = data.to_dict(orient="records")

        GRID_SIZE = 100
        SMOOTH_DIAGRAM = 1

        data_tsne = np.array([[item["tsne_x"], item["tsne_y"]] for item in data])

        bin_sample_ls = self._find_bins_2d(data_tsne, GRID_SIZE)

        bin_len_stat = [[len(sublist) for sublist in row] for row in bin_sample_ls]

        thres = list(np.unique(sorted(np.array(bin_len_stat).reshape(-1)))[::2])
        thres.append(np.array(bin_len_stat).max())

        entropy_ls_width = []
        for thre in thres[1:]:
            loc = np.where(bin_len_stat < thre)
            zero_bin_ls = [[loc[0][i], loc[1][i]] for i in range(len(loc[0]))]
            space_entropy = self._calculate_spatial_entropy(
                data_tsne,
                GRID_SIZE,
                smooth_diagram=SMOOTH_DIAGRAM,
                smooth=True,
                zero_bin_ls=zero_bin_ls,
            )
            entropy_ls_width.append(space_entropy)

        entropy_ls_width = self._entropy_filter(entropy_ls_width)
        quantiles = [2, 4]

        edge_width = self._find_edge_ids(
            np.log(entropy_ls_width),
            self._cal_cut_thre(np.log(entropy_ls_width), quantiles),
        )
        edge = edge_width[0]

        loc = np.where(bin_len_stat < thres[edge + 1])
        zero_bin_ls = [[loc[0][i], loc[1][i]] for i in range(len(loc[0]))]
        space_entropy = self._calculate_spatial_entropy(
            data_tsne,
            GRID_SIZE,
            smooth_diagram=SMOOTH_DIAGRAM,
            smooth=True,
            zero_bin_ls=zero_bin_ls,
        )
        sample_id_ls_tmp = copy.deepcopy(bin_sample_ls)

        for i in zero_bin_ls:
            sample_id_ls_tmp[i[0]][i[1]] = []

        sample_id_ls_tmp_flatten = []
        for i in sample_id_ls_tmp:
            for j in i:
                sample_id_ls_tmp_flatten.extend(j)
        sample_ls_tmp = [
            data[i] for i in sample_id_ls_tmp_flatten if isinstance(i, int)
        ]
        import pyarrow as pa

        table = pa.Table.from_pylist(sample_ls_tmp)
        return ray.data.from_arrow(table)
