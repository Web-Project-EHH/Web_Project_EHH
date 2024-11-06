from fastapi.templating import Jinja2Templates
from common.auth import get_current_user
from services import users_services

class CustomJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str):
        super().__init__(directory=directory)
        self.env.globals['get_user'] = self.get_user_from_request
        self.env.globals['get_user_by_id'] = users_services.get_user_by_id

    def get_user_from_request(self, request):
        return get_current_user(request.cookies.get('token'))