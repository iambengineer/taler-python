from typing import TypeAlias
from pydantic import BaseModel, ConfigDict

ErrorCode: TypeAlias = int


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="allow")
    code: ErrorCode
    hint: str
    detail: str | None = None
    parameter: str | None = None
    path: str | None = None

class TalerError(Exception):
    def __init__(self, http_status, error_detail):
        self.http_status = http_status
        self.error_detail = error_detail
        msg = f'{self.__class__.__name__}({self.http_status}): [{self.error_detail.code}] {self.error_detail.hint}'
        super().__init__(msg)

class NotFoundError(TalerError):
    def __init__(self, error_detail):
        super().__init__(404, error_detail)

class ConflictError(TalerError):
    def __init__(self, error_detail):
        super().__init__(409, error_detail)

class GoneError(TalerError):
    def __init__(self, error_detail):
        super().__init__(410, error_detail)


class UnauthorizedError(TalerError):
    def __init__(self, error_detail):
        super().__init__(401, error_detail)

class ForbiddenError(TalerError):
    def __init__(self, error_detail):
        super().__init__(403, error_detail)


ErrorStatusCodes = {
    404: NotFoundError,
    409: ConflictError,
    410: GoneError,
    401: UnauthorizedError,
    403: ForbiddenError,
}

def raise_for_taler_error(response):
    if response.status_code < 400:
        return
    e = ErrorDetail.model_validate(response.json())
    error_type = ErrorStatusCodes.get(response.status_code)
    if error_type is None:
        raise TalerError(response.status_code, e)
    raise error_type(e)