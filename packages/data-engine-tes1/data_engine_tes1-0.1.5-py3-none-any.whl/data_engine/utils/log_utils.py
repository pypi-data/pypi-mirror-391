import os
import json
import datetime
from pathlib import Path
import socket
import uuid
import pandas as pd
import threading
import numpy as np
import pandas as pd
import pyarrow as pa


# 反序列化查看原始数据
def deserialize(d):
    # if isinstance(d, dict):
    #     return {k: default_serializer(v) for k, v in d.items()}

    """递归处理数据结构，将复杂类型转换为Spark可识别的原生类型"""
    if isinstance(d, dict):
        return {k: default_serializer(v) for k, v in d.items()}
    elif isinstance(d, (list, tuple)):
        return [default_serializer(item) for item in d]
    else:
        return default_serializer(d)
    return d


def default_serializer(obj):
    # bytes -> UTF-8 字符串
    if isinstance(obj, bytes):
        return obj.decode("utf-8")

    # numpy 标量
    if isinstance(obj, np.generic):
        return obj.item()

    # numpy 数组
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # pandas Series / DataFrame
    if isinstance(obj, pd.Series):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")

    # pyarrow Scalar
    if isinstance(obj, pa.Scalar):
        return obj.as_py()

    # pyarrow Array / ChunkedArray
    if isinstance(obj, (pa.Array, pa.ChunkedArray)):
        return obj.to_pylist()

    # pyarrow Table
    if isinstance(obj, pa.Table):
        return obj.to_pydict()

    # 其他类型，直接返回字符串
    return str(obj)


class RayDataErrorLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, base_dir="/tmp/ray_data_errors", session_id=None):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._init(base_dir, session_id)
                cls._instance = instance
        return cls._instance

    def _init(self, base_dir, session_id):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        import ray

        self.session_id = session_id or ray.get_runtime_context().get_job_id()

        self.log_dir = Path(base_dir) / self.session_id
        self.log_dir.mkdir(parents=True, exist_ok=True)

        hostname = socket.gethostname()
        self.worker_id = f"{hostname}_{os.getpid()}"
        self.log_file_path = (
            self.log_dir / f"error_records_worker_{self.worker_id}.jsonl"
        )

    def log_error(self, record, error_msg, process_name=None):
        """
        record: pd.Series, pd.DataFrame, or dict
        """
        entries = []

        if isinstance(record, pd.Series):
            entries = [record.to_dict()]
        elif isinstance(record, pd.DataFrame):
            entries = record.head(10).to_dict(orient="records")
        elif isinstance(record, dict):
            entries = [record]
        else:
            raise ValueError("Unsupported record type")
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            result = []
            for entry in entries:
                error_entry = {
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "data": entry,
                    "error": error_msg,
                    "worker": self.worker_id,
                    "process_name": process_name,
                }

                result.append(
                    json.dumps(
                        error_entry, ensure_ascii=False, default=default_serializer
                    )
                )
            f.write("\n".join(result))
