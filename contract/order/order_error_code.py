from enum import IntEnum


class OrderErrorCode(IntEnum):
    NOT_FOUND = 20001
    CANNOT_DELETE = 20002
    LOCKED = 20003
    CONFLICT = 20004  # 乐观锁冲突：并发修改

