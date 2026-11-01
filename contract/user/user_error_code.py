from enum import IntEnum


class UserErrorCode(IntEnum):
    """用户错误码（12xxx）"""

    NOT_FOUND = 12001
    ACCOUNT_EXISTS = 12002
    ACCOUNT_IN_USE = 12003
    CANNOT_DELETE_ENABLED = 12004
    CREATE_USER_FAILED = 12005
    UPDATE_USER_FAILED = 12006
