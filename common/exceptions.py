from fastapi import HTTPException

class ConflictException(HTTPException):
    def __init__(self, status_code: int = 409, detail: str = "Conflict"):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(HTTPException):
    def __init__(self, status_code: int = 404, detail: str = "Not Found"):
        super().__init__(status_code=status_code, detail=detail)

class ForbiddenException(HTTPException):
    def __init__(self, status_code: int = 403, detail: str = "Forbidden"):
        super().__init__(status_code=status_code, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, status_code: int = 400, detail: str = "Bad Request"):
        super().__init__(status_code=status_code, detail=detail)