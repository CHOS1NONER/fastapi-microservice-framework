"""全局错误处理中间件"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from common.utils.domain_error import DomainError
from common.utils.logger_helper import LoggerHelper
from common.utils.rpc_error import RpcError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数验证错误处理"""
    trace_id = getattr(request.state, "trace_id", "unknown")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "参数验证失败",
            "errors": exc.errors(),
            "trace_id": trace_id
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    trace_id = getattr(request.state, "trace_id", "unknown")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "trace_id": trace_id
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger = LoggerHelper.logger_obj if LoggerHelper.logger_obj else None
    trace_id = getattr(request.state, "trace_id", "unknown")
    
    if logger:
        logger.exception(f"[{trace_id}] Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "trace_id": trace_id
        }
    )

async def rpc_exception_handler(request: Request, exc: RpcError):
    logger = LoggerHelper.logger_obj if LoggerHelper.logger_obj else None
    trace_id = getattr(request.state, "trace_id", "unknown")

    if logger:
        logger.error(
            f"[{trace_id}] RPC error: [{exc.service_name}] {exc.code} - {exc.msg}"
        )

    return JSONResponse(
        status_code=200,
        content={
            "code": exc.code,
            "message": exc.msg,
            "trace_id": trace_id,
        },
    )


async def domain_exception_handler(request: Request, exc: DomainError):
    trace_id = getattr(request.state, "trace_id", "unknown")

    return JSONResponse(
        status_code=200,
        content={
            "code": exc.code if hasattr(exc, "code") else -1,
            "message": exc.msg,
            "trace_id": trace_id
        }
    )

