from typing import Protocol

from contract.user.user_dto import UserAuthModel


class UserPort(Protocol):
    """
    鉴权侧需要的用户能力契约。
    可注入 UserService 类（classmethod）或任意实现了同签名方法的对象。
    """

    def get_user_auth_by_account(self, account: str) -> UserAuthModel | None:
        """按账号查询含密码哈希的鉴权模型；不存在返回 None。"""
        ...
