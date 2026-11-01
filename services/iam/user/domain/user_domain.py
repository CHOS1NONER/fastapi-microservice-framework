from datetime import datetime, timedelta

from contract.user.user_dto import UserAuthModel
from contract.user.user_enum import UserStatusEnum
from services.iam.user.models.user import User


class UserDomain:
    @staticmethod
    def is_enabled(user: User | UserAuthModel) -> bool:
        return user.status == UserStatusEnum.ENABLE

    @staticmethod
    def is_new_user(
        user: User | UserAuthModel, *, days: int = 7, now: datetime | None = None
    ) -> bool:
        if user.create_time is None:
            return False
        now = now or datetime.now()
        create_time = user.create_time
        if isinstance(create_time, str):
            create_time = datetime.fromisoformat(create_time)
        return now - create_time < timedelta(days=days)
