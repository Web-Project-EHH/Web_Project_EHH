from typing import Optional, Literal, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from common.exceptions import NotFoundException, BadRequestException
from data.models.reply import Reply, ReplyResponse
from data.models.user import User
from services import replies_services, votes_services, users_services
from datetime import datetime


router = APIRouter(prefix='/replies', tags=['Replies'])


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
                   offset: int = Query(default=0, ge=0)) -> List[Reply] | Reply:

    replies = replies_services.get_replies(reply_id=reply_id, text=text, user_name=user_name, user_id=user_id, topic_id=topic_id,
                                           topic_title=topic_title, sort_by=sort_by, sort=sort, start_date=start_date,
                                           end_date=end_date, limit=limit, offset=offset)
    
    if not replies:
        raise NotFoundException(detail='No matching replies found')
    
    return replies


@router.get('/{id}', response_model=Reply)
def get_reply_by_id(reply_id: int):
      
    reply = replies_services.get_replies(reply_id=reply_id)
                 
    if not reply:
          raise NotFoundException(detail='Reply not found')
    
    return reply
    

@router.post('/', response_model=Reply)
def create_reply(reply: Reply, current_user: User = Depends(users_services.get_current_user)) -> Reply:

        reply = replies_services.create(reply, current_user)

        if not reply:
            raise BadRequestException(detail='The reply could not be created')
        
        return reply

@router.post('/{reply_id}/vote', response_model=None)
def vote(reply_id: int, user_id: int, type: bool) -> JSONResponse:
    
    vote = votes_services.vote(reply_id=reply_id, user_id=user_id,type=type)
                                    
    if not vote:
        raise BadRequestException('Vote could not be registered')
    
    elif vote == 'upvoted':
        return JSONResponse(content={'message':'You have upvoted'}, status_code=200)
    
    elif vote == 'downvoted':
          return JSONResponse(content={'message':'You have downvoted'}, status_code=200)
    
    elif vote == 'vote deleted':
          return JSONResponse(content={'message':'Vote has been deleted'}, status_code=200)


@router.put('/', response_model=None)
def edit_reply(old_reply: ReplyResponse, new_reply: ReplyResponse, 
               current_user: User=Depends(users_services.get_current_user)) -> ReplyResponse:

	edited = replies_services.edit_text(old_reply, new_reply, current_user)

	if not edited:
		raise BadRequestException(detail='Reply could not be edited')

	return edited


@router.delete('/', response_model=None)
def delete_reply(reply_id: int, current_user: User=Depends(users_services.get_current_user)) -> JSONResponse:
    
    deleted = replies_services.delete(reply_id, current_user)
    
    if not deleted:
        raise BadRequestException(detail='Reply could not be deleted')
    
    return JSONResponse(content={'message':'Reply has been deleted'}, status_code=200)
