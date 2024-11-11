from common.exceptions import NotFoundException
from data.database import read_query, update_query
from data.models.user import User
from services import replies_services, users_services


def vote(reply_id: int, type: bool, current_user: User) -> str | None:

    """
    Cast a vote on a reply by a user. The vote can be an upvote or a downvote, or get deleted if the user has
    voted the same way already.

    Args:
        reply_id (int): The ID of the reply being voted on.
        user_id (int): The ID of the user casting the vote.
        type (bool): The type of vote. True for upvote, False for downvote.

    Returns:
        str | None: A message indicating the result of the vote action. Possible values are:
            - 'vote deleted': If the user had already voted with the same type and the vote was deleted.
            - 'upvoted': If the vote was cast as an upvote.
            - 'downvoted': If the vote was cast as a downvote.
            - None: If no action was taken (e.g., if the reply does not exist).

    Raises:
        NotFoundException: If the reply with the given reply_id does not exist.
    """
    
    if not replies_services.exists(reply_id):
        raise NotFoundException(detail='Reply not found')
    
    current_vote = users_services.has_voted(reply_id=reply_id, user_id=current_user.id)
    response = None

    if current_vote: # Check if the there is a vote already and:
        
        if current_vote.type == type: # if it's the same type, delete it
            deleted_vote = update_query('''DELETE FROM votes WHERE user_id = ? AND reply_id = ?''', (current_user.id, reply_id))
            
            if deleted_vote:
                response = 'vote deleted'
        
        else: # change it, if it's a different type
            changed_vote = update_query('''UPDATE votes SET type = ? WHERE user_id = ? AND reply_id = ?''', (type, current_user.id, reply_id))
            if changed_vote:
                response = 'upvoted' if type else 'downvoted'
    
    else: # Otherwise create a new vote
        vote = update_query('''INSERT INTO votes (user_id, reply_id, type) VALUES(?, ?, ?)''', (current_user.id, reply_id, type))
       
        if vote:
            response = 'upvoted' if type else 'downvoted'
        
    return response


def get_votes(reply_id: int):
    
    votes = read_query('''SELECT CAST(SUM(CASE WHEN type = 0 THEN -1 ELSE type END) AS INT)  FROM votes WHERE reply_id = ?''', (reply_id,))

    if votes:

        votes = votes[0][0]

        return votes if isinstance(votes, int) and votes != 0 else ''
    
    return ''