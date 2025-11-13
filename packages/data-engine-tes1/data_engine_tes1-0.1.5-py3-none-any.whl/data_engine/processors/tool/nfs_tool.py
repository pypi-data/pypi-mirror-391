import os
import shutil
import logging
from typing import Optional, List, Dict, Any

import pandas as pd
import ray

from data_engine.core.base import BaseMapper, BaseReader


logger = logging.getLogger(__name__)


class ToolNfsMeta(BaseReader):
    """
    扫描目录下的文件
    扫描目录下的文件，返回文件路径列表。
    """

    def __init__(
        self,
        root_dir: str,
        file_extensions: str = None,
        media_type: str = None,
        num_blocks: int = None,
        **kwargs,
    ):
        """
        Args:
            root_dir: 根目录#根目录
            file_extensions: 需要过滤的文件扩展名#需要过滤的文件扩展名
            media_type: 如果 file_extensions 为空，可根据媒体类型设置默认扩展名（目前仅支持 video）
            num_blocks: block 数量#block 数量
        """
        super().__init__(**kwargs)

        self.root_dir = os.path.abspath(root_dir)
        self.file_extensions = (
            [ext.lower() for ext in file_extensions] if file_extensions else None
        )
        if num_blocks:
            self.num_blocks = num_blocks
        if self.file_extensions is None and media_type == "video":
            self.file_extensions = [
                ".mp4",
                ".avi",
                ".mkv",
                ".mov",
                ".flv",
                ".wmv",
                ".webm",
                ".mpeg",
                ".mpg",
                ".3gp",
                ".ts",
            ]

    def run(self, data):
        file_paths = []
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if self.file_extensions and ext[1:].lower() not in self.file_extensions:
                    continue
                file_paths.append(os.path.join(dirpath, filename))

        df = pd.DataFrame({"path": file_paths})

        executor_type = self._engine_config.get("executor", "ray")
        if executor_type == "ray":
            if hasattr(self, "num_blocks") and self.num_blocks is not None:
                return ray.data.from_pandas(df, override_num_blocks=self.num_blocks)
            else:
                return ray.data.from_pandas(df)
        elif executor_type == "spark":
            from data_engine.core.factory import ExecutorFactory

            executor = ExecutorFactory.create_executor("spark")
            records = df.to_dict("records")
            sc = executor.spark.sparkContext
            if hasattr(self, "num_blocks") and self.num_blocks is not None:
                rdd = sc.parallelize(records, self.num_blocks)
            else:
                rdd = sc.parallelize(records)
            return rdd


class ToolNfsDelete(BaseMapper):
    """
    删除指定路径文件。
    删除指定路径文件。
    """

    def __init__(self, col_name: str = "path", **kwargs):
        """
        初始化方法
        col_name: 需要删除的路径字段名#需要删除的路径字段名
        """
        self.col_name = col_name
        super().__init__(**kwargs)

    def _delete_one(self, path: str):
        """删除单个文件"""
        if not path:
            return
        abs_path = os.path.abspath(path)
        if os.path.isfile(abs_path):
            os.remove(abs_path)
            logger.debug(f"Deleted file: {abs_path}")
        else:
            logger.debug(f"Skip delete, not a file: {abs_path}")

    def process(self, data):
        """处理单个数据项，支持字符串或列表"""
        value = data.get(self.col_name)

        if isinstance(value, list):
            for p in value:
                self._delete_one(p)
        elif isinstance(value, str):
            self._delete_one(value)
        else:
            raise TypeError(
                f"{self.col_name} 必须是 str 或 list[str] 类型，实际为 {type(value)}"
            )

        return data


class ToolNfsFileSize(BaseMapper):
    """
    文件大小
    获取文件大小。
    """

    def __init__(
        self,
        path_field: str = "path",
        size_field: str = "size",
        unit: str = "M",
        **kwargs,
    ):
        """
        初始化方法
        path_field: 计算大小的路径的字段#计算大小的路径的字段
        size_field: 结果保存字段#结果保存字段
        unit: 转换单位，支持B(字节)、K(KB)、M(MB)、G(GB)，默认M
        """
        super().__init__(**kwargs)
        self.path_field = path_field
        self.size_field = size_field
        # 单位转换系数（1单位对应的字节数）
        self.unit_converters = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3}
        # 验证单位合法性，默认使用M
        self.unit = unit.upper() if unit.upper() in self.unit_converters else "M"

    def process(self, data: Dict[str, Any]):
        file_path = data.get(self.path_field)
        size = os.path.getsize(file_path)
        target_size = size / self.unit_converters[self.unit]
        data[self.size_field] = f"{round(target_size, 3)}{self.unit}"
        return data


class ToolNfsCopy(BaseMapper):
    """
    文件复制
    文件复制
    """

    def __init__(
        self,
        src_root: str,
        col_name: str = "path",
        dest_root: str = None,
        overwrite: bool = True,
        **kwargs,
    ):
        """
        初始化方法
        src_root: 源文件根目录#源文件根目录
        col_name: 需要转换的字段名#需要转换的字段名
        dest_root: 目标文件根目录#目标文件根目录（默认为工作空间workspace）
        overwrite: 是否允许覆盖#是否允许覆盖
        """
        super().__init__(**kwargs)
        self.col_name = col_name
        self.src_root = os.path.abspath(src_root)
        self.dest_root = os.path.abspath(dest_root or os.environ.get("workspace", "."))
        self.overwrite = overwrite

    def _copy_one(self, source_path: str) -> str:
        """复制单个文件并返回目标路径"""
        source_path = os.path.abspath(source_path)

        # 校验 source_path 是否在 src_root 下
        if (
            not self.src_root.startswith(self.src_root)
            or os.path.commonpath([source_path, self.src_root]) != self.src_root
        ):
            raise ValueError(f"Path {source_path} 不在 src_root {self.src_root} 下")

        rel_path = os.path.relpath(source_path, self.src_root)
        dest_path = os.path.join(self.dest_root, rel_path)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if not self.overwrite and os.path.exists(dest_path):
            logger.debug(f"Skip copy, file exists: {dest_path}")
        else:
            shutil.copy2(source_path, dest_path)
            logger.debug(f"Copied {source_path} -> {dest_path}")

        return dest_path

    def process(self, data):
        """处理单个数据项，支持路径或路径列表"""
        value = data[self.col_name]

        if isinstance(value, list):
            dest_list = [self._copy_one(p) for p in value]
            data[self.col_name] = dest_list
        elif isinstance(value, str):
            data[self.col_name] = self._copy_one(value)
        else:
            raise TypeError(
                f"{self.col_name} 必须是 str 或 list[str] 类型，实际为 {type(value)}"
            )

        return data


class ToolAbsToRel(BaseMapper):
    """
    绝对路径转换为相对路径
    将绝对路径转换为相对路径
    """

    def __init__(self, base_root: str = None, col_name: str = "path", **kwargs):
        """
        初始化方法
        base_root: 用作参考的根路径#用作参考的根路径
        col_name: 需要转换的字段名#需要转换的字段名
        """
        super().__init__(**kwargs)
        self.col_name = col_name
        workspace = os.environ["workspace"]
        if not base_root:
            base_root = workspace
        else:
            base_root = base_root.strip()
            if not base_root.startswith(workspace):
                base_root = os.path.join(workspace, base_root)
        self.base_root = base_root

    def _convert_one(self, abs_path: str) -> str:
        """将单个绝对路径转换为相对路径"""
        abs_path = os.path.abspath(abs_path)
        if os.path.commonpath([abs_path, self.base_root]) != self.base_root:
            raise ValueError(f"Path {abs_path} 不在 base_root {self.base_root} 下")

        return os.path.relpath(abs_path, self.base_root)

    def process(self, data):
        """处理单个数据项，支持字符串或列表"""
        value = data[self.col_name]

        if isinstance(value, list):
            data[self.col_name] = [self._convert_one(p) for p in value]
        elif isinstance(value, str):
            data[self.col_name] = self._convert_one(value)
        else:
            raise TypeError(
                f"{self.col_name} 必须是 str 或 list[str] 类型，实际为 {type(value)}"
            )

        return data


class ToolRelToAbs(BaseMapper):
    """
    相对路径转换为绝对路径
    将相对路径转换为绝对路径
    """

    def __init__(self, base_root: str = None, col_name: str = "path", **kwargs):
        """
        初始化方法
        base_root: 相对路径的基准根目录#相对路径的基准根目录
        col_name: 需要转换的字段名#需要转换的字段名
        """
        super().__init__(**kwargs)
        self.col_name = col_name
        datasource_root = os.environ["datasource_root"]
        if not base_root:
            base_root = datasource_root
        else:
            base_root = base_root.strip()
            if not base_root.startswith(datasource_root):
                base_root = os.path.join(datasource_root, base_root)
        self.base_root = os.path.abspath(base_root)

    def _convert_one(self, rel_path: str) -> str:
        """将单个相对路径转换为绝对路径"""
        if os.path.isabs(rel_path):
            abs_path = os.path.abspath(rel_path)
            if os.path.commonpath([abs_path, self.base_root]) != self.base_root:
                raise ValueError(f"Path {abs_path} 不在 base_root {self.base_root} 下")
            return abs_path

        return os.path.abspath(os.path.join(self.base_root, rel_path))

    def process(self, data: Dict[str, Any]):
        """处理单个数据项，支持字符串或列表"""
        value = data[self.col_name]

        if isinstance(value, list):
            data[self.col_name] = [self._convert_one(p) for p in value]
        elif isinstance(value, str):
            data[self.col_name] = self._convert_one(value)
        else:
            raise TypeError(
                f"{self.col_name} 必须是 str 或 list[str] 类型，实际为 {type(value)}"
            )

        return data


class ToolNfsRename(BaseMapper):
    """
    文件重命名
    将文件重命名为新的文件名（保留扩展名，不改变目录）。
    """

    def __init__(
        self,
        col_name: str = "path",
        new_name_field: str = "new_name",
        overwrite: bool = False,
        **kwargs,
    ):
        """
        初始化方法
        Args:
            col_name: 原始路径字段名#指数据中存储文件路径的字段名称（例如"path"）
            new_name_field: 用于替换的新名称字段名（不含扩展名） # 需从数据行中已有的该字段取值，作为文件名的新名称部分（不包含文件后缀）
            overwrite: 是否允许覆盖已有文件#是否允许覆盖已有文件
        """
        super().__init__(**kwargs)
        self.col_name = col_name
        self.new_name_field = new_name_field
        self.overwrite = overwrite

    def process(self, data: Dict[str, Any]):
        old_path = os.path.abspath(data[self.col_name])
        new_name = str(data.get(self.new_name_field))

        if not new_name:
            raise ValueError(f"缺少新的文件名字段: {self.new_name_field}")

        dir_path = os.path.dirname(old_path)
        _, ext = os.path.splitext(old_path)  # 保留旧的扩展名
        new_path = os.path.join(dir_path, new_name + ext)

        # 如果目标文件存在且不允许覆盖
        if os.path.exists(new_path) and not self.overwrite:
            raise FileExistsError(f"目标文件已存在: {new_path}")

        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        os.rename(old_path, new_path)
        logger.info(f"toolnfs renamed {old_path} -> {new_path}")

        # 更新路径字段
        data[self.col_name] = new_path
        return data


class ToolNfsExt(BaseMapper):
    """
    提取文件扩展名
    从文件路径中提取扩展名，保存到指定字段。
    """

    def __init__(
        self,
        path_field: str = "path",
        ext_field: str = "ext",
        keep_dot: bool = False,
        lowercase: bool = True,
        **kwargs,
    ):
        """
        初始化方法
        Args:
            path_field: 源路径字段名#源路径字段名
            ext_field: 扩展名结果字段名#扩展名结果字段名
            keep_dot: 是否保留"."#是否保留"."
            lowercase: 是否转为小写#是否转为小写
        """
        super().__init__(**kwargs)
        self.path_field = path_field
        self.ext_field = ext_field
        self.keep_dot = keep_dot
        self.lowercase = lowercase

    def process(self, data: Dict[str, Any]):
        file_path = str(data.get(self.path_field, ""))
        if not file_path:
            data[self.ext_field] = ""
            return data

        _, ext = os.path.splitext(file_path)
        if not self.keep_dot:
            ext = ext[1:]  # 去掉"."

        if self.lowercase:
            ext = ext.lower()

        data[self.ext_field] = ext
        return data
