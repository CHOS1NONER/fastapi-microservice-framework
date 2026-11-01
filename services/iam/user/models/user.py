from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from common.base.base_table_model import BaseTableModel
from contract.user.user_enum import UserStatusEnum


class User(BaseTableModel):
    account: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, comment="账号"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码"
    )
    status: Mapped[UserStatusEnum] = mapped_column(
        Integer,
        nullable=False,
        default=UserStatusEnum.ENABLE,
        comment="状态",
    )
    user_name: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="用户名"
    )
