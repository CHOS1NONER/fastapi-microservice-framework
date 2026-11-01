from loguru import logger


class AlchemyLogger:

    def __init__(self, content: logger):
        self.__content = content

    @property
    def content(self):
        return self.__content

    @property
    def error(self):
        return self.__content.error

    @property
    def info(self):
        return self.__content.info

    @property
    def exception(self):
        return self.__content.exception

    @property
    def warning(self):
        return self.__content.warning

    @property
    def debug(self):
        return self.__content.debug
