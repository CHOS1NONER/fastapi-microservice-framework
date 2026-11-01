import os
import shutil


class FileUtils:
    @staticmethod
    def try_create_dir(file_path: str) -> str:
        """
        尝试去创建目录

        :param file_path: 文件路径
        """
        try:
            arr = file_path.split("/")
            arr.pop()
            file_dir_path = "/".join(arr)
            if not os.path.exists(file_dir_path):
                os.makedirs(file_dir_path)
            return file_dir_path
        except Exception:
            pass
        return None

    @staticmethod
    def try_create_empty_file(file_path: str):
        """
        尝试去创建一个空文件

        :param file_path: 文件路径
        """
        FileUtils.try_create_dir(file_path)
        with open(file_path, "w", encoding="utf-8"):
            pass

    @staticmethod
    def delete_dir(dir_path: str):
        """
        删除目录

        :param dir_path: 目录路径
        """
        arr = dir_path.split("/")
        arr.pop()
        file_dir_path = "/".join(arr)
        if os.path.exists(file_dir_path):
            shutil.rmtree(file_dir_path)
