from fastapi import HTTPException

class ConflictException(HTTPException):
    def __init__(self, detail, status_code: int = 409):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(HTTPException):
    def __init__(self, detail, status_code: int = 404):
        super().__init__(status_code=status_code, detail=detail)

class ForbiddenException(HTTPException):
    def __init__(self, detail, status_code: int = 403):
        super().__init__(status_code=status_code, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class UnauthorizedException(HTTPException):
    def __init__(self, detail, status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)     