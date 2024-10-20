from common.exceptions import ForbiddenException, NotFoundException
from data.database import update_query
from services import replies_services, users_services


def vote(reply_id: int, user_id: int, type: bool):

    """
    Casts a vote on a reply by a user. If the user has already voted on the reply, 
    it updates or deletes the vote based on the current vote type.
    
    Args:
        reply_id (int): The ID of the reply being voted on.
        user_id (int): The ID of the user casting the vote.
        type (bool): The type of vote (True for upvote, False for downvote).
    
    Raises:
        NotFoundException: If the reply does not exist.
    
    Returns:
        String: A response indicating the result of the vote action.
    """
    
    if not replies_services.exists(reply_id):
        raise NotFoundException(detail='Reply not found')
    
    current_vote = users_services.has_voted(reply_id=reply_id, user_id=user_id)
    response = None

    if current_vote:
        
        if current_vote.type == type:
            deleted_vote = update_query('''DELETE FROM votes WHERE user_id = ? AND reply_id = ?''', (user_id, reply_id))
            
            if deleted_vote:
                response = 'vote deleted'
        
        else:
            changed_vote = update_query('''UPDATE votes SET type = ? WHERE user_id = ? AND reply_id = ?''', (type, user_id, reply_id))
            if changed_vote:
                if type == True:
                    response = 'upvoted'
                elif type == False:
                    response = 'downvoted'
    
    else:
        vote = update_query('''INSERT INTO votes (user_id, reply_id, type) VALUES(?, ?, ?)''', (user_id, reply_id, type))
       
        if vote:
            if type == True:
                    response = 'upvoted'
            elif type == False:
                response = 'downvoted'
        

    return response