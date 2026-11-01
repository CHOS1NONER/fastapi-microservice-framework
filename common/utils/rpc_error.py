class RpcError(Exception):
    """跨服务调用业务失败（统一 Response.code != SUCCESS）时抛出。"""

    def __init__(self, msg: str, code: int = 6000, service_name: str = ""):
        self.msg = msg
        self.code = code
        self.service_name = service_name
        super().__init__(self.msg)
