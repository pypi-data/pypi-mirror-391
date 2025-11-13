from ray.data.datasource import FilenameProvider


class NameProvider(FilenameProvider):

    def __init__(self, file_format: str):
        self.file_format = file_format

    def get_filename_for_block(self, block, write_uuid, task_index, block_index):
        return f"{write_uuid}_{task_index:06}_{block_index:06}" f".{self.file_format}"
