"""链路追踪中间件"""
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from common.utils.logger_helper import LoggerHelper


class TracingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件，生成trace_id"""

    async def dispatch(self, request: Request, call_next):
        # 生成或获取trace_id
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        request.state.trace_id = trace_id

        # 记录请求开始时间
        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 计算耗时
        process_time = time.time() - start_time

        # 添加响应头
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Process-Time"] = str(process_time)

        # 只记录超过5秒的请求日志
        if process_time > 5:
            logger = LoggerHelper.logger_obj if LoggerHelper.logger_obj else None
            if logger:
                logger.warning(
                    f"[{trace_id}] {request.method} {request.url.path} - "
                    f"{response.status_code} - {process_time:.3f}s"
                )

        return response

