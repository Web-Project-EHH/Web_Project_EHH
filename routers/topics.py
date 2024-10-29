from fastapi import APIRouter, HTTPException, Query
from services import topics_services
from typing import Optional, Literal
# да се импортне auth като е готово

from data.models.topic import Topic, TopicCreate, TopicUpdate, TopicResponse
from services.topics_services import exists

topics_router = APIRouter(prefix='/topics',tags=['Topics'])

@topics_router.get('/')
def get_all_topics(
        sort: Optional[str] = Query(
            None, description="Specify the order of topics ('asc' for ascending, 'desc' for descending)."
        ),
        sort_by: Optional[str] = Query('topic_id', description="Topic can be sorted by id, title, user, status, category"),
        search: Optional[str] = None,
        username: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[Literal['open', 'closed']] = None
        ):

    status_value = 1 if status == "open" else 0 if status == "closed" else None

    if status and status.lower() not in ['open', 'closed']:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    if sort and sort.lower() not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort parameter"
        )

    if sort_by and sort_by.lower() not in ['topic_id', 'title', 'user_id', 'status', 'category_id']:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort by parameter"
        )


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int):

    topic = topics_services.fetch_topic_by_id(topic_id)

    if not topic:
        raise HTTPException(
            status_code=404,
            detail='Topic does not exists'
        )

@topics_router.post('/')
def create_topic(new_topic: TopicCreate, user_id):
    # проверка на юзър/
    # проверка на категория дали съществува, дали е заключена, дали категорията е private
    #ако е прайвет дали юзъра е админ
    topic = topics_services.create_new_topic(new_topic,user_id)

@topics_router.patch('/{topic_id}/best_reply')
def update_topic_best_reply(topic_id: int, current_user, topic_update: TopicUpdate):
    if not topic_update.best_reply_id:
        raise HTTPException(status_code=400, detail='No best reply id provided')

    topic_replies = topics_services.fetch_replies_for_topic(topic_id)

    if not topic_replies:
        raise HTTPException(status_code=404, detail='Topic does not have replies')

    if topic_update.best_reply_id in topic_replies:
        return topics_services.update_best_reply_for_topic(topic_id, topic_update.best_reply_id)

    else:
        raise HTTPException(status_code=404, detail='Reply does not exist')

@topics_router.patch('/{topic_id}/locking')
def lock_topic(topic_id: int, user):
    topic = topics_services.fetch_topic_by_id(topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail='Topic does not exist')

    if not user.is_admin and topic.user_id != user.user_id:
        raise HTTPException(status_code=403, detail='You are not allowed to lock this topic')

    topics_services.lock_or_unlock_topic(topic_id)
    if topic.is_locked == 1:
        return f'Topic {topic_id} is locked'
    else:
        return f'Topic {topic_id} is unlocked'
