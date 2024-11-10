import re
from fastapi import APIRouter, Body, Form, HTTPException, Query, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
# from data.models.category import Category
from data.models.reply import ReplyCreate, ReplyCreateWeb
from services import categories_services, replies_services, topics_services, users_services
from typing import Optional
import common.auth
from common.exceptions import BadRequestException, ForbiddenException
from data.models.topic import TopicCreate, TopicBestReplyUpdate
from services.topics_services import fetch_all_topics, verify_topic_owner
from common.template_config import CustomJinja2Templates
from mariadb import IntegrityError


router = APIRouter(prefix='/topics',tags=['Topics'])
templates = CustomJinja2Templates(directory="templates")

#WORKS
@router.get('/create', response_model=None)
def create_topic_page(request: Request):
    return templates.TemplateResponse(
        name='create-topic.html',
        request=request,
        context={'categories': categories_services.get_categories_with_write_access_only(user=common.auth.get_current_user(request.cookies.get('token')))}
    )

#WORKS
@router.get('/', response_model=None)
def get_topics(
    request: Request = None,
    search: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    token = request.cookies.get('token')
    current_user = common.auth.get_current_user(token)
    
    if not current_user:
        return templates.TemplateResponse(
            name='topics.html',
            context={
                'request': request,
                'token': token,
                'error': 'You must be logged in to view topics.'
            }
        )

    categories = categories_services.get_categories(limit=10000, current_user=current_user)
    
    topics = fetch_all_topics(
        search=search,
        username=username,
        category=category,
        status=status,
        sort=sort,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
        current_user=current_user
    )

    return templates.TemplateResponse(
        name='topics.html',
        context={
            'topics': topics['topics'],
            'token': token,
            'categories': categories,
            'current_page': topics['current_page'],
            'total_pages': topics['total_pages'],
            'request': request,
            'per_page': per_page,
        }
    )

#WORKS
@router.get('/{topic_id}', response_model=None)
def get_topic_replies(
    request: Request,
    topic_id: int
):
    """
    GET /topics/{topic_id}
    Fetches the details of a specific topic including its replies.
    """
    current_user = common.auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(
            name='topics.html',
            context={'request': request, 'error': 'You must be logged in to view topics.'}
        )

    token = request.cookies.get('token')
    
    topic = topics_services.fetch_topic_by_id(topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail='Topic not found')
    
    replies = topics_services.fetch_replies_for_topic(topic_id)

    return templates.TemplateResponse(
        name='single-topic.html',
        context={
            'topic': topic, 
            'replies': replies, 
            'current_user': current_user, 
            'token': token, 
            'request': request
        },
    )

#WORKS
@router.post('/create', response_model=None)
def create_topic(new_topic: TopicCreate = Depends(topics_services.topic_create_form), request: Request = None):
    """
    POST /topics/create
    Creates a new topic and renders the appropriate HTML template.
    Parameters:
    - `new_topic` (TopicCreate): New topic details.
    - `request` (Request): Request object.
    Returns:
    - Redirects to the newly created topic page on success.
    - Renders an error page if the creation fails.
    """
    user = common.auth.get_current_user(request.cookies.get('token'))

    category_id = new_topic.category_id

    if not users_services.check_user_access_level(user.id, category_id) == 2:
        return templates.TemplateResponse(name='error.html', context={'error': 'User not authorised'}, request=request)

    if user is None:
        return templates.TemplateResponse(name='topics.html', context={'error': 'User not authorised'}, request=request)

    try:
        topic_data = topics_services.create_new_topic(new_topic, user.id)
        
        if "topic_id" not in topic_data:
            raise HTTPException(status_code=500, detail="topic_id was not returned by create_new_topic")


        if topic_data == 'User does not exist':
            return templates.TemplateResponse("error.html", {"request": request, "message": "User does not exist"})
        
        if topic_data == 'Category does not exist':
            return templates.TemplateResponse("error.html", {"request": request, "message": "Category does not exist"})
        
        return RedirectResponse(url=f"/topics/{topic_data['topic_id']}", status_code=303)
    
    except HTTPException as http_exc:
        error_message = re.sub(r"^Validation error:\s*(\w+:\s*)?", "", http_exc.detail)
        return templates.TemplateResponse("error.html", {"request": request, "message": error_message})

    except Exception as exc:
        return templates.TemplateResponse("error.html", {"request": request, "message": "An unexpected error occurred."})
    
#WORKS
@router.post('/{topic_id}/best_reply', response_model=None)
async def update_topic_best_reply(
    topic_id: int,
    request: Request,
    best_reply_data: dict = Body(...),
):
    token = request.cookies.get('token')
    user = common.auth.get_current_user(token)

    if not user:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'message': 'User not authorised'}
        )

    topic = topics_services.fetch_topic_by_id(topic_id)
    if not topic:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'message': 'Topic not found'}
        )

    if not verify_topic_owner(user.id, topic_id):
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'message': 'User not authorised'}
        )

    topic_replies = topics_services.fetch_replies_for_topic(topic_id)
    if not topic_replies:
        return templates.TemplateResponse(
            name='topics.html',
            context={'request': request, 'error': 'No replies found'}
        )

    best_reply_id = int(best_reply_data.get('best_reply_id'))

    if best_reply_id and best_reply_id in [reply.id for reply in topic_replies]:
        topics_services.update_best_reply_for_topic(topic_id, best_reply_id)
        return RedirectResponse(url=f"/topics/{topic_id}", status_code=303)

    return templates.TemplateResponse(
        name='error.html',
        context={'request': request, 'message': 'Reply ID not found'}
    )

#not working
@router.patch('/{topic_id}/locking')
def lock_topic(topic_id: int, request: Request = None):
    """
    PATCH /topics/{topic_id}/locking
    Locks or unlocks a topic.
    Parameters:
    - `topic_id` (int): ID of the topic to lock/unlock.
    - `user` (UserAuthDep): Current user details.
    Returns:
    - 200 OK: Topic locked/unlocked successfully.
    - 403 Forbidden: User is not allowed to lock the topic.
    - 404 Not Found: Topic does not exist.
    """
    user = common.auth.get_current_user(request.cookies.get('token'))

    topic = topics_services.fetch_topic_by_id(topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail='Topic does not exist')

    if not user.is_admin:
        raise HTTPException(status_code=403, detail='You are not allowed to lock this topic')

    new_lock_status = not topic.is_locked

    topics_services.lock_or_unlock_topic(topic_id, new_lock_status)

    return 


#WORKS
@router.delete('/{topic_id}', response_model=None)
def delete_topic(topic_id: int, request: Request = None):

    user = common.auth.get_current_user(request.cookies.get('token'))

    if not user.is_admin:
        return templates.TemplateResponse(name='topics.html', context={'error': 'User not authorised'}, request=request)

    try:

        result = topics_services.delete_topic(topic_id)

        if not result:
            raise BadRequestException(detail='Topic could not be deleted')
        
        elif result == f"Topic {topic_id} deleted successfully":
            return JSONResponse({'message': 'Topic deleted successfully'}, status_code=200)
        
    except IntegrityError:
        raise ForbiddenException(detail='Topic could not be deleted')


@router.post('/{topic_id}/create', response_model=None)
async def create_reply(request: Request):

    current_user = common.auth.get_current_user(request.cookies.get('token'))

    reply_data = await request.form()

    topic_id = int(reply_data.get('topic_id'))

    text = reply_data.get('text')

    reply = ReplyCreateWeb(text=text, topic_id=topic_id, user_id=current_user.id)

    reply = replies_services.create(reply, current_user)
     
    return RedirectResponse(url=f"/topics/{topic_id}", status_code=303)