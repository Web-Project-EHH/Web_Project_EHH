from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from common import auth
from services import categories_services, users_services
from common.template_config import CustomJinja2Templates
from data.models.user import UserRegistration


router = APIRouter(prefix='/users', tags=['User'])
templates = CustomJinja2Templates(directory="templates")


@router.get('/{user_id}/permissions', response_model=None)
def serve_permissions(user_id: int, request: Request = None):

    current_user = auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})

    if not current_user.is_admin:
        return templates.TemplateResponse(name="error.html", request=request, context={'error': 'You do not have permission to view this page.'})
    
    categories = categories_services.get_categories(current_user=current_user, limit=10000)

    user = users_services.get_user_by_id(user_id)
    return templates.TemplateResponse(name="permissions.html", request=request, context={'user': user, 'categories': categories})


@router.delete('/{user_id}/delete', response_model=None)
def delete_user_by_id(user_id: int, request: Request):

    current_user = auth.get_current_user(request.cookies.get('token'))
    if not current_user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})

    if current_user.id != user_id:
        return templates.TemplateResponse(name="error.html", request=request, context={'error': 'You do not have permission to delete this account.'})

    users_services.delete_user(user_id)
    return JSONResponse(content={'message': 'User deleted successfully'}, status_code=200)


@router.get('/me')
def get_current_user_me(request: Request):
    user = auth.get_current_user(request.cookies.get('token'))
    return templates.TemplateResponse(name="profile.html", request=request, context={'user': user})


@router.get('/', response_model=None)
def serve_users(request: Request):

    user = auth.get_current_user(request.cookies.get('token'))

    if not user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})
    
    return templates.TemplateResponse(name="users.html", request=request)


@router.get('/register', response_model=None)
def serve_register (request: Request):
    return templates.TemplateResponse(name="register.html", request=request)


@router.post('/register', response_model=None)
def register_user(request: Request = None, register: UserRegistration = Depends(users_services.get_registration)):
    if users_services.get_user(register.username):
        return templates.TemplateResponse(name="register.html", request=request, context={'error': 'User already exists'})

    if users_services.email_exists(register.email):
        return templates.TemplateResponse(name="register.html", request=request, context={'error': 'Email already exists'})

    if register.password != register.confirm_password:
        return templates.TemplateResponse(name="register.html", request=request, context={'error': 'Passwords do not match'})
    
    hashed_password = auth.get_password_hash(register.password) 
    register.password = hashed_password
    user_id = users_services.create_user(register)
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie('token', auth.create_access_token(data={'sub': register.username, 'is_admin': False, "id": user_id}))
    return response
    

@router.get('/login', response_model=None)
def serve_login(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@router.post('/login', response_model=None)
def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    user = auth.authenticate_user(form_data.username, form_data.password)

    if not user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'Invalid username or password'})
    
    is_admin = user.is_admin
    id = user.id

    access_token = auth.create_access_token(data={'sub': user.username, 'is_admin': is_admin, "id": id})
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie('token', access_token)
    return response


@router.post('/logout')
def logout(request: Request = None):
    token = request.cookies.get('token')
    auth.token_blacklist.add(token)
    response = RedirectResponse(url='/', status_code=302)
    response.delete_cookie('token')
    return response


@router.get('/search', response_model=None)
def search_users(request: Request, username: str = Query(...)):

    current_user = auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})

    users = users_services.get_users_by_username(username)
    return templates.TemplateResponse(request=request, name="users.html", context={'users': users})

@router.get('/{user_id}', response_model=None)
def get_user_by_id(user_id: int, request: Request = None):

    current_user = auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})

    user = users_services.get_user_by_id(user_id)
    return templates.TemplateResponse(name="user_profile.html", request=request, context={'user': user})


@router.post('/{user_id}/permissions')
async def update_permissions(user_id: int, request: Request):
    current_user = auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "You need to login."})

    if not current_user.is_admin:
        return templates.TemplateResponse("error.html", {"request": request, "error": "You do not have permission."})

    form_data = await request.form()
    
    # Parse the form data into a structured dictionary
    permissions = {}
    for key, value in form_data.multi_items():
        if key.startswith("permissions"):
            # Extract the category ID from the key
            parts = key.strip('permissions[]').split('][')
            category_id = parts[0]  # e.g. '1' from 'permissions[1][category_id]'
            field = parts[1]  # 'category_id' or 'access_level'

            if category_id not in permissions:
                permissions[category_id] = {}

            # Store the value under the appropriate field
            permissions[category_id][field] = value

    # Now `permissions` is a dictionary where the key is category_id
    # and the value is another dictionary with 'category_id' and 'access_level'
    for category_id, permission in permissions.items():
        access_level = permission.get('access_level')
        users_services.update_user_permissions(user_id=user_id, category_id=category_id, access_level=access_level)

    return RedirectResponse(url=f'/users/{user_id}/permissions', status_code=302)
