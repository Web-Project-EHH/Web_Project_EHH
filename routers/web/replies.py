from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from common.exceptions import BadRequestException
from common.template_config import CustomJinja2Templates
from data.models.reply import Reply, ReplyCreate, ReplyEdit, ReplyEditID
from data.models.user import User
from services import replies_services, votes_services
from datetime import datetime
import common.auth



router = APIRouter(prefix='/replies', tags=['Replies'])
templates = CustomJinja2Templates(directory="templates")

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
                   offset: int = Query(default=0, ge=0), request: Request = None,
                   current_user: User = Depends(common.auth.get_current_user)):
    replies = replies_services.get_replies(reply_id=reply_id, text=text, user_name=user_name, user_id=user_id, topic_id=topic_id,
                                           topic_title=topic_title, sort_by=sort_by, sort=sort, start_date=start_date,
                                           end_date=end_date, limit=limit, offset=offset)
    
    
    return templates.TemplateResponse(name='replies.html', context={'replies': replies, 'user': current_user}, request=request)


@router.get('/{id}', response_model=Reply)
def get_reply_by_id(reply_id: int, request: Request = None, current_user: User = Depends(common.auth.get_current_user)):
      
    reply = replies_services.get_replies(reply_id=reply_id)
    
    return templates.TemplateResponse(name='single-reply.html', context={'reply': reply, 'user': current_user}, request=request)
    

@router.post('/{reply_id}/vote', response_model=None)
async def vote(request: Request, reply_id: int):

    current_user = common.auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name='error.html', context={'error': 'You must be logged in to vote'}, request=request)
    
    vote = await request.form()
    vote = int(vote['vote'])
    vote = True if vote == 1 else False


    vote = votes_services.vote(reply_id=reply_id, type=vote, current_user=current_user)

    referer = request.headers.get("referer")
                                    
    if not vote:
         raise BadRequestException('Vote could not be registered')
    
    elif vote == 'upvoted':
         return RedirectResponse(url=referer, status_code=303)
    
    elif vote == 'downvoted':
         return RedirectResponse(url=referer, status_code=303) 
      
    elif vote == 'vote deleted':
        return RedirectResponse(url=referer, status_code=303)


@router.patch('/', response_model=None)
def edit_reply(old_reply: ReplyEditID, new_reply: ReplyEdit, 
               current_user: User=Depends(common.auth.get_current_user), request: Request = None):

	edited = replies_services.edit_text(old_reply, new_reply, current_user)

	return templates.TemplateResponse(name='single-reply.html', context={'reply': edited, 'user': current_user}, request=request)

@router.delete('/{reply_id}/delete', response_model=None)
def delete_reply(reply_id: int, request: Request):

     current_user = common.auth.get_current_user(request.cookies.get('token'))

     reply = replies_services.get_reply_by_id(reply_id=reply_id)

     if not current_user:
         return templates.TemplateResponse(name='error.html', context={'error': 'User not authorised'}, request=request)
     
     if not (current_user.id == reply.user_id or not current_user.is_admin):
         return templates.TemplateResponse(name='error.html', context={'error': 'User not authorised'}, request=request)
     
     replies_services.delete(reply_id, current_user)
     
     return RedirectResponse(url=f'/topics/{reply.topic_id}', status_code=303)


