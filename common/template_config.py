from fastapi.templating import Jinja2Templates
from common.auth import get_current_user
from services import categories_services, replies_services, users_services

class CustomJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str):
        super().__init__(directory=directory)
        self.env.globals['get_user'] = self.get_user_from_request
        self.env.globals['get_user_by_id'] = users_services.get_user_by_id
        self.env.globals['check_access'] = users_services.check_user_access_level
        self.env.globals['get_category_by_id'] = categories_services.get_by_id
        self.env.globals['get_reply_by_id'] = replies_services.get_reply_by_id
    
    def get_user_from_request(self, request):
        return get_current_user(request.cookies.get('token'))