"""Stable domain error codes, decoupled from transports."""
class ObservatoryError(Exception):
    def __init__(self, code: str, message: str, status: int = 422):
        self.code, self.status = code, status
        super().__init__(message)


def require(condition, code: str, message: str, status: int = 422):
    if not condition:
        raise ObservatoryError(code, message, status)
