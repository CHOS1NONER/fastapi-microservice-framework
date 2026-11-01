from common.base.base_crud import BaseCRUD
from contract.user.user_dto import GetUserListParams
from services.iam.user.models.user import User


class UserCRUD(BaseCRUD[User]):
    model = User

    async def page_list(self, params: GetUserListParams):
        stmt = self._statement()
        if params.status:
            stmt = stmt.where(User.status == params.status.value)
        if params.account:
            stmt = stmt.where(User.account.like(f"%{params.account}%"))
        return await self.paginate(stmt, page_index=params.page_index, page_size=params.page_size)
