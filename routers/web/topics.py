from fastapi import APIRouter, HTTPException, Query, Request, Depends
# from data.models.category import Category
from services import topics_services
from typing import Optional, List
import common.auth
from common.exceptions import NotFoundException, UnauthorizedException
from services.categories_services import get_by_id, is_private
from data.models.topic import TopicCreate, TopicBestReplyUpdate, TopicResponse
from services.topics_services import fetch_all_topics, verify_topic_owner, fetch_topic_by_id
from common.template_config import CustomJinja2Templates
from data.models.user import User
from services.replies_services import get_replies


router = APIRouter(prefix='/topics',tags=['Topics'])
templates = CustomJinja2Templates(directory="templates")

@router.get('/', response_model=None)
def get_topics(
    request: Request = None,
    search: Optional[str] = Query(None, description="Search by topic title"),
    username: Optional[str] = Query(None, description="Filter by username of the topic creator"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    status: Optional[str] = Query(None, description="Filter by topic status: 'open' or 'closed'"),
    sort: Optional[str] = Query(None, description="Sort order: 'asc' or 'desc' (use with sort_by)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by, e.g., 'topic_id', 'user_id'"),
):
    """
    GET /topics
    Fetches a list of all topics, filtered by optional criteria.
    """

    token = request.cookies.get('token')

    topics = fetch_all_topics(
        search=search,
        username=username,
        category=category,
        status=status,
        sort=sort,
        sort_by=sort_by
    )


    return templates.TemplateResponse(
        name='topics.html',
        context={'topics': topics, 'token': token},
        request=request
    )

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

    token = request.cookies.get('token')
    
    topic = topics_services.fetch_topic_by_id(topic_id)

    replies = get_replies(topic_id=topic_id)

    if not topic:
        raise NotFoundException(detail='Topic not found')
    
    if not replies:
        return []

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
@router.post('/')
def create_topic(new_topic: TopicCreate, user: User = Depends(common.auth.get_current_user)):
    """
    POST /topics
    Creates a new topic.
    Parameters:
    - `new_topic` (TopicCreate): New topic details.
    - `user` (UserAuthDep): Current user details.
    Returns:
    - 201 Created: Topic created successfully.
    - 400 Bad Request: User does not exist or category does not exist.
    """
    
    topic = topics_services.create_new_topic(new_topic, user.id)

    if topic == 'User does not exist':
        raise HTTPException(
            status_code=400,
            detail='User does not exist'
        )
    
    if topic == 'Category does not exist':
        raise HTTPException(
            status_code=400,
            detail='Category does not exist'
        )
    
    return HTTPException(status_code=201, detail='Topic created successfully')


#WORKS
@router.patch('/{topic_id}/best_reply')
def update_topic_best_reply(topic_id: int, topic_update: TopicBestReplyUpdate, current_user: User = Depends(common.auth.get_current_user)):
    """
    PATCH /topics/{topic_id}/best_reply
    Updates the best reply for a topic.
    Parameters:
    - `topic_id` (int): ID of the topic to update.
    - `current_user` (UserAuthDep): Current user details.
    - `topic_update` (TopicUpdate): New best reply ID.
    Returns:
    - 200 OK: Best reply updated successfully.
    - 400 Bad Request: No best reply ID provided.
    - 403 Forbidden: User is not allowed to set the best reply.
    - 404 Not Found: Topic or reply does not exist.
    """
    if not topic_update.best_reply_id:
        raise HTTPException(status_code=400, detail='No best reply id provided')

    topic = topics_services.fetch_topic_by_id(topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail='Topic does not exist')

    if not verify_topic_owner(current_user.id, topic_id):
        raise HTTPException(status_code=403, detail='You are not allowed to set the best reply for this topic')

    topic_replies = topics_services.fetch_replies_for_topic(topic_id)

    if not topic_replies:
        raise HTTPException(status_code=404, detail='Topic does not have replies')

    reply_ids = [reply[0] for reply in topic_replies]

    if topic_update.best_reply_id in reply_ids:
        return topics_services.update_best_reply_for_topic(topic_id, topic_update.best_reply_id)
    else:
        raise HTTPException(status_code=404, detail='Reply does not exist') 
    

#WORKS    
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
        # and topic.user_id != user.id:
        raise HTTPException(status_code=403, detail='You are not allowed to lock this topic')

    new_lock_status = not topic.is_locked

    topics_services.lock_or_unlock_topic(topic_id, new_lock_status)

    return 

