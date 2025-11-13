from typing import Optional, Union
from enum import Enum

from .executors import HuggingFaceExecutor, RayExecutor, SparkExecutor
from .base import Executor
from data_engine.define import ExecutorType

instance = None


class ExecutorFactory:
    """Factory class for creating executors."""

    @staticmethod
    def create_executor(
        executor_type: Union[str, ExecutorType], config: dict = None, **kwargs
    ) -> Executor:
        """Create an executor of the specified type.

        Args:
            executor_type: The type of executor to create
            **kwargs: Additional arguments to pass to the executor constructor

        Returns:
            The created executor

        Raises:
            ValueError: If the executor type is not supported
        """
        executor_type = ExecutorType.from_str(executor_type)
        global instance
        if instance:
            return instance

        if executor_type == ExecutorType.HF:
            instance = HuggingFaceExecutor(config)
        elif executor_type == ExecutorType.RAY:
            instance = RayExecutor(config)
        elif executor_type == ExecutorType.SPARK:
            instance = SparkExecutor(config)
        else:
            raise ValueError(f"Unsupported executor type: {executor_type}")
        return instance
