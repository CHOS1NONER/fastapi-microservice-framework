from common.cache.redis_cache import CacheKey, redis_cache
from common.utils.domain_error import DomainError
from common.utils.password_helper import hash_password
from contract.user.user_dto import (
    DeleteUserParams,
    GetUserByFieldsRequest,
    GetUserListParams,
    GetUserParams,
    PostUserParams,
    UpdateUserParams,
    UserAuthModel,
    UserListDTO,
    UserModel,
    UserPageDTO,
    UserStatusSwitch,
)
from contract.user.user_error_code import UserErrorCode
from services.iam.user.crud.user_crud import UserCRUD
from services.iam.user.domain.user_domain import UserDomain

RDS_USER = CacheKey("user:{params.id}")


class UserService:
    user_crud = UserCRUD()

    @classmethod
    async def get_user_by_fields(cls, fields: GetUserByFieldsRequest) -> UserListDTO:
        filters = fields.model_dump(exclude_none=True, mode="json")
        data = await cls.user_crud.get_by_fields(**filters)
        return UserListDTO(items=[UserModel(**item.to_dict()) for item in data])

    @classmethod
    async def get_user_auth_by_account(cls, account: str) -> UserAuthModel | None:
        users = await cls.user_crud.get_by_fields(account=account)
        if not users:
            return None
        return UserAuthModel(**users[0].to_dict())

    @classmethod
    @redis_cache.cache(RDS_USER)

    async def get_user_by_id(cls, params: GetUserParams) -> UserModel:
        user = await cls.user_crud.get_by_id(params.id)
        if user is None:
            raise DomainError(code=UserErrorCode.NOT_FOUND, msg="用户不存在")
        return UserModel(**user.to_dict())

    @classmethod
    async def page_list(cls, params: GetUserListParams) -> UserPageDTO:
        page_user_result = await cls.user_crud.page_list(params)
        rows = [UserModel(**item.to_dict()) for item in page_user_result["rows"]]
        return UserPageDTO(total=page_user_result["total"], rows=rows)

    @classmethod
    async def create_user(cls, params: PostUserParams) -> UserModel:
        if await cls.user_crud.get_by_fields(account=params.account):
            raise DomainError(code=UserErrorCode.ACCOUNT_EXISTS, msg="账号已存在")

        user = await cls.user_crud.create(
            account=params.account,
            user_name=params.user_name,
            password=await hash_password(params.password),
            status=params.status,
        )
        return UserModel(**user.to_dict())

    @classmethod
    @redis_cache.invalidate(RDS_USER)
    async def update_user(cls, params: UpdateUserParams) -> UserModel:
        user = await cls.user_crud.get_by_id(params.id)
        if user is None:
            raise DomainError(code=UserErrorCode.NOT_FOUND, msg="用户不存在")

        if params.account and params.account != user.account:
            exists = await cls.user_crud.get_by_fields(account=params.account)
            if exists and exists[0].id != params.id:
                raise DomainError(code=UserErrorCode.ACCOUNT_IN_USE, msg="账号已被其他用户使用")

        user.account = params.account
        return UserModel(**user.to_dict())

    @classmethod
    @redis_cache.invalidate(RDS_USER)
    async def remove_user(cls, params: DeleteUserParams) -> bool:
        user = await cls.user_crud.get_by_id(params.id)
        if user is None:
            raise DomainError(code=UserErrorCode.NOT_FOUND, msg="用户不存在")
        if UserDomain.is_enabled(user):
            raise DomainError(code=UserErrorCode.CANNOT_DELETE_ENABLED, msg="用户状态正常，不允许删除")

        await cls.user_crud.remove(user)
        return True

    @classmethod
    @redis_cache.invalidate(RDS_USER)
    async def switch_status(cls, params: UserStatusSwitch) -> bool:
        user = await cls.user_crud.get_by_id(params.id)
        if user is None:
            raise DomainError(code=UserErrorCode.NOT_FOUND, msg="用户不存在")
        user.status = params.status
        return True
