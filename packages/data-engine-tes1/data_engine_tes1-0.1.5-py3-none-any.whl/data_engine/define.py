from enum import Enum
from typing import Optional


class OpType(Enum):
    FILTER = "filter"
    MAPPER = "mapper"
    CONSUMER = "consumer"
    READER = "reader"
    TOOL = "tool"


class ExecutorType(Enum):
    """Enum for supported executor types."""

    HF = "hf"
    RAY = "ray"
    SPARK = "spark"

    @classmethod
    def from_str(cls, name) -> "ExecutorType":
        if isinstance(name, cls):
            return name
        try:
            if not name:
                name = "ray"
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Unknown ExecutorType: {name},reason:{e}")
