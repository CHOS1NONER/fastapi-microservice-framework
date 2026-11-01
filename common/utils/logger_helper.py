import os
import sys

from loguru import logger

from common.utils.alchemy_logger import AlchemyLogger
from common.utils.file_utils import FileUtils


class LoggerHelper:
    CRITICAL = 1
    ERROR = 2
    INFO = 3
    WARNING = 4
    DEBUG = 5
    TRACE = 6
    FATAL = 7

    logger_obj = None
    logger_pid = None
    logger_level = None

    @staticmethod
    def bind_error_callback(handle):
        if LoggerHelper.logger_obj is None:
            return
        logger.add(handle, level='ERROR')

    @staticmethod
    def new_logger(name: str,
                   file_name: str | None = None,
                   level=5,
                   file_save_count: str = '90 days') -> AlchemyLogger:
        """
        新建一个日志对象。linux不输出stream，windows不输出file
        路径转小写
        目录不存在要创建目录
        按日期切片

        :param name: 日志名
        :param file_name: 日志文件名
        :param level: 日志显示等级
        :param file_save_count: 日志文件保存多少个
        :return: 返回日志对象
        """
        # if level != LoggerHelper.FATAL:
        #     print(name, file_name, os.getcwd(), os.getpid())

        if LoggerHelper.logger_obj is not None and os.getpid() == LoggerHelper.logger_pid:
            return LoggerHelper.logger_obj
        LoggerHelper.logger_pid = os.getpid()

        level_str = 'DEBUG'
        if level == LoggerHelper.CRITICAL:
            level_str = 'CRITICAL'
        elif level == LoggerHelper.ERROR:
            level_str = 'ERROR'
        elif level == LoggerHelper.WARNING:
            level_str = 'WARNING'
        elif level == LoggerHelper.INFO:
            level_str = 'INFO'
        elif level == LoggerHelper.TRACE:
            level_str = 'TRACE'
        elif level == LoggerHelper.FATAL:
            level_str = 'CRITICAL'
        LoggerHelper.logger_level = level_str

        formatter = \
            "{time:YYYY-MM-DD HH:mm:ss}-{name}.{file}-[line:{line}]-[pid:{process}]-{level}-[Message]: {message}"

        if sys.platform != 'win32':
            logger.remove(handler_id=None)
            FileUtils.try_create_dir(file_name)
            logger.add(file_name + '.{time:YYYY-MM-DD}' + '.log',
                       level=level_str,
                       format=formatter,
                       encoding="utf-8",
                       rotation='00:00',
                       retention=file_save_count,
                       )
        else:
            logger.remove()
            # 仅限本地开发使用
            formatter = \
                "{time:YYYY-MM-DD HH:mm:ss}-{name}.{file}-[line:{line}]-[pid:{process}]-{level}-[Message]: {message}"
            logger.add(sys.stderr,
                       level=level_str,
                       format=formatter)

        obj = AlchemyLogger(logger)
        LoggerHelper.logger_obj = obj

        return obj
