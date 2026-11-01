from pydantic import BaseModel, Field

from contract.g_dto import ListResult, PageResult
from contract.user.user_enum import UserStatusEnum


class GetUserByFieldsRequest(BaseModel):
    account: str | None = Field(None, description="账号")
    status: UserStatusEnum | None = Field(None, description="状态")
    create_time: str | None = Field(None, description="创建时间")
    update_time: str | None = Field(None, description="更新时间")


class UserModel(BaseModel):
    id: int = Field(..., description="用户ID")
    account: str = Field(..., description="账号")
    user_name: str = Field(..., description="用户名")
    status: UserStatusEnum | None = Field(default=None, description="状态")
    create_time: str | None = Field(None, description="创建时间")
    update_time: str | None = Field(None, description="更新时间")


class UserAuthModel(BaseModel):
    """内部鉴权模型（含密码哈希），仅供 IAM 内部登录校验使用，不对外暴露。"""

    id: int = Field(..., description="用户ID")
    account: str = Field(..., description="账号")
    user_name: str = Field(..., description="用户名")
    password: str = Field(..., description="密码哈希")
    status: UserStatusEnum | None = Field(default=None, description="状态")
    create_time: str | None = Field(default=None, description="创建时间")


# 统一复用 common 的泛型分页/列表包装，避免各模块重复定义
UserListDTO = ListResult[UserModel]
UserPageDTO = PageResult[UserModel]


class UpdateUserParams(BaseModel):
    id: int = Field(..., description="用户ID")
    account: str = Field(..., description="账号")


class DeleteUserParams(BaseModel):
    id: int = Field(..., description="用户ID")


class GetUserParams(BaseModel):
    id: int = Field(..., description="用户ID")


class GetUserListParams(BaseModel):
    page_index: int
    page_size: int
    account: str | None = None
    status: UserStatusEnum | None = None


class PostUserParams(BaseModel):
    account: str = Field(..., description="账号")
    user_name: str = Field(..., description="名称")
    status: UserStatusEnum = Field(..., description="状态")
    password: str = Field(..., description="密码")


class UserStatusSwitch(BaseModel):
    id: int
    status: UserStatusEnum
