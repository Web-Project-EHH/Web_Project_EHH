from fastapi.templating import Jinja2Templates
from common.auth import get_current_user

class CustomJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str):
        super().__init__(directory=directory)
        self.env.globals['get_user'] = get_current_user
