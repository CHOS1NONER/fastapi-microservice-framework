from pydantic import BaseModel, Field

from contract.g_enum import ResponseCode


class Response[T](BaseModel):
    code: ResponseCode = Field(ResponseCode.SUCCESS, description="状态码")
    data: T | None = Field(default=None, description="数据")
    msg: str = Field(default="", description="消息")


class ListResult[T](BaseModel):
    """通用列表返回。各模块统一复用，不要再自定义列表包装。"""

    items: list[T] = Field(default_factory=list, description="数据列表")


class PageResult[T](BaseModel):
    """通用分页返回。各模块统一复用，不要再自定义分页包装。"""

    total: int = Field(0, description="总数")
    rows: list[T] = Field(default_factory=list, description="当前页数据")
