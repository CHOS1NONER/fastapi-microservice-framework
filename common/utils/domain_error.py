class DomainError(Exception):
    """业务域异常。必须传错误码；文案可选，仅作可读说明。"""

    def __init__(self, code: int, msg: str = ""):
        self.code = int(code)
        self.msg = msg
        super().__init__(self.code, self.msg)
