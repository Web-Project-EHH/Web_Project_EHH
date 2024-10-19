from typing import Optional, Literal, List
from fastapi import APIRouter, HTTPException, Query
from common.exceptions import NotFoundException, BadRequestException
from data.models.reply import Reply
from services import replies_services
from datetime import datetime

router = APIRouter(prefix='/replies')

@router.get('/', response_model=None)
def get_replies(reply_id: Optional[int] = Query(default=None), 
                   text: Optional[str] = Query(default=None), 
                   user_name: Optional[str] = Query(default=None),
                   user_id: Optional[int] = Query(default=None),
                   topic_id: Optional[int] = Query(default=None),
                   topic_title: Optional[str] = Query(default=None),
                   sort_by: Literal['user_id', 'topic_id', 'created'] = Query(default=None),
                   sort: Literal['desc', 'asc'] = Query(default=None),
                   start_date: Optional[datetime] = Query(default=None),
                   end_date: Optional[datetime] = Query(default=None),
                   limit: int = Query(default=10, ge=1),
                   offset: int = Query(default=0, ge=0)) -> List[Reply] | Reply | HTTPException:

    replies = replies_services.get_replies(reply_id=reply_id, text=text, user_name=user_name, user_id=user_id, topic_id=topic_id,
                                           topic_title=topic_title, sort_by=sort_by, sort=sort, start_date=start_date,
                                           end_date=end_date, limit=limit, offset=offset)
    
    if not replies:
        raise NotFoundException(detail='No matching replies found')
    
    return replies
    

@router.post('/', response_model=Reply)
def create_reply(reply: Reply) -> Reply | HTTPException:

        reply = replies_services.create(reply)

        if not reply:
            raise BadRequestException(detail='The reply could not be created')
        
        return reply
    


