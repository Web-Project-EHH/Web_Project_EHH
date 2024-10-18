from fastapi import Response


class BadRequest(Response):
    def __init__(self, message, status_code=400):
        super().__init__(message, status_code)

class Unauthorized(Response):
    def __init__(self, message, status_code=401):
        super().__init__(message, status_code)

class Forbidden(Response):
    def __init__(self, message, status_code=403):
        super().__init__(message, status_code)

class NotFound(Response):
    def __init__(self, message, status_code=404):
        super().__init__(message, status_code)

class Conflict(Response):
    def __init__(self, message, status_code=409):
        super().__init__(message, status_code)

class ServerError(Response):
    def __init__(self, message, status_code=500):
        super().__init__(message, status_code)

class NoContent(Response):
    def __init__(self, status_code=204):
        super().__init__(status_code)

class SuccessfullResponse(Response):
    def __init__(self, message, status_code=200):
        super().__init__(message, status_code)
