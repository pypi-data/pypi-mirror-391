from data_engine.core.base import BaseTool
import os, hashlib


class ToolMd5(BaseTool):
    """
    对指定字段生成 MD5

    该类用于对输入数据字典中的某个字段进行 MD5 加密，可以增强数据安全性。
    当 `add_salt=True` 时，会在原始值前加入盐值再进行哈希计算，并将盐值存储到指定字段。
    """

    def __init__(
        self,
        column_name: str = "text",
        add_salt: bool = True,
        salt_column_name: str = "salt",
        salt: str = "salt",
        **kwargs,
    ):
        """
        column_name: 需要md5的列名称#需要md5的列名称
        add_salt: 是否加盐#是否加盐
        salt: 默认盐值#默认盐值
        salt_column_name: 盐保存的字段名#盐保存的字段名
        """
        super().__init__(**kwargs)
        self.column_name = column_name
        self.add_salt = add_salt
        self.salt = salt
        self.salt_column_name = salt_column_name

    def process(self, data: dict):
        if self.column_name not in data:
            raise KeyError(f"Column '{self.column_name}' not found in input data")

        value = str(data[self.column_name])  # 确保是字符串
        hash_obj = hashlib.md5()

        if self.add_salt:
            salt = self.salt
            if not salt:
                salt = os.urandom(16).hex()  # 生成16字节随机盐并转成字符串
            hash_obj.update(salt.encode("utf-8"))
            data[self.salt_column_name] = salt

        hash_obj.update(value.encode("utf-8"))
        data[f"{self.column_name}_md5"] = hash_obj.hexdigest()

        return data
