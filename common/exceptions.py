class ConflictException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class NotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ForbiddenException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)