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
import math
import ray

from data_engine.core.base import BaseFilter, BaseTool


class NlpFilterDataOptimization(BaseTool):
    """
    指令数据集联合优化
    综合loss、标签数目和语义空间分布优化指令数据集
    后训练数据合成专用算法
    """

    only_ray = True

    def __init__(self, target_total: str, grid_size: str = None, **kwargs):
        """
        初始化方法:
            target_total:数量#选取数据子集的数目
            grid_size:格子数目#用于分析数据分布的广泛性
        """
        super().__init__(**kwargs)
        self.target_total = target_total
        self.grid_size = grid_size

    def _sort_data_by_log_sum(self, data):
        data_list = []
        for i, item in enumerate(data):
            loss = item["loss"]
            calculate_tags = item["calculate_tags"]
            item["sort_key"] = math.log(loss) + calculate_tags  # math.log()
            data_list.append(item)
        sorted_data = sorted(data_list, key=lambda x: x["sort_key"], reverse=True)
        return sorted_data

    def _analyze_grid_distribution(self, points, grid_size=100):
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        # 获取坐标范围
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)
        # 使用 np.histogram2d 统计每个网格的点数量
        counts, x_edges, y_edges = np.histogram2d(
            x_coords, y_coords, bins=grid_size, range=[[x_min, x_max], [y_min, y_max]]
        )
        counts = counts.astype(int)
        grid_info = {}
        for idx, (x, y) in enumerate(points):
            row = np.searchsorted(x_edges, x, side="right") - 1
            col = np.searchsorted(y_edges, y, side="right") - 1
            if (row, col) not in grid_info:
                grid_info[(row, col)] = []
            grid_info[(row, col)].append(idx)
        return counts, grid_info

    def _select_n_samples_with_priority(self, data, grid_info, target_total):

        # 对网格按照点数量从大到小排序
        sorted_cells = sorted(grid_info.items(), key=lambda x: len(x[1]), reverse=True)
        selected_indices = set()
        total_selected = 0
        for rank, (cell, indices) in enumerate(sorted_cells):
            if total_selected >= target_total:
                break
            # 确定当前格子的取点数量规则
            if rank < 1000:  # Top 1000
                to_select = min(5, len(indices))
            elif rank < 2000:  # Top 1000-2000
                to_select = min(3, len(indices))
            else:  # 其他
                to_select = min(1, len(indices))

            # 选择数据
            selected_indices.update(indices[:to_select])
            total_selected = len(selected_indices)

            # 如果达到目标总数，提前退出
            if total_selected >= target_total:
                break
        selected_data = [data[i] for i in selected_indices]
        return selected_data

    def run(self, data):
        data = data.to_pandas()
        data = data.to_dict(orient="records")
        data_tsne = np.array([[item["tsne_x"], item["tsne_y"]] for item in data])
        data = self._sort_data_by_log_sum(data)
        counts, grid_info = self._analyze_grid_distribution(data_tsne, self.grid_size)
        selected_data = self._select_n_samples_with_priority(
            data, grid_info, self.target_total
        )
        import pyarrow as pa

        table = pa.Table.from_pylist(selected_data)

        return ray.data.from_arrow(table)
