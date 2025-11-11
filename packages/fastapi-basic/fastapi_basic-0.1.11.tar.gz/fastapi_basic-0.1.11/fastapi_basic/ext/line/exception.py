from fastapi import status
from ...exception.base_exception import InternalBaseException


class LineBotException(InternalBaseException):
    def __init__(self, message: str = "", **kwargs):
        status_code: int = status.HTTP_502_BAD_GATEWAY
        code: str = "line_bot_error"
        log_message: str = "Line bot error"

        message = f"{log_message}, {message}" if message else log_message
        super().__init__(status_code=status_code, code=code, message=message, **kwargs)
