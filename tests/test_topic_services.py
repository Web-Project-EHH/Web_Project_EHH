from unittest import TestCase
from unittest.mock import patch
from data.models.topic import TopicResponse, TopicCreate
from services import topics_services as topics


#TOPIC
TOPIC_ID = 1
TITLE = 'just a title'
USER_ID = 1
AUTHOR = 'just a man'
STATUS_OPEN = 0
BEST_REPLY_ID = None
CATEGORY_ID = 1
CATEGORY_NAME = 'Uncategorized'


def create_topic(topic_id, topic_title=TITLE, author=AUTHOR):
    return TopicResponse(
        topic_id=topic_id,
        title=topic_title,
        user_id=USER_ID,
        author=author,
        is_locked=STATUS_OPEN,
        best_reply_id=BEST_REPLY_ID,
        category_id=CATEGORY_ID,
        category_name=CATEGORY_NAME)

  
class TopicsServices_Should(TestCase):
   
    def test_getById_returnsTopicResponseObject_whenExists(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            mock_read_query.return_value = [
                (TOPIC_ID, TITLE, USER_ID, AUTHOR, STATUS_OPEN, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME)
            ]

            expected = create_topic(TOPIC_ID)
            
            result = topics.fetch_topic_by_id(TOPIC_ID)
            
            self.assertEqual(expected, result)
    
    
    def test_getById_returnsNone_whenNoSuchTopic(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            topic_id = 1
            mock_read_query.return_value = []

            expected = None
            result = topics.fetch_topic_by_id(topic_id)

            self.assertEqual(expected, result)
          
        
    def test_exists_returns_True_when_topicIsPresent(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            mock_read_query.return_value = [(1)]
        
            result = topics.exists(TOPIC_ID)
        
            self.assertTrue(result)
               
               
    def test_exists_returns_False_when_noTopic(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            mock_read_query.return_value = []
        
            result = topics.exists(TOPIC_ID)
        
            self.assertFalse(result)
            
              
    def test_create_returnsTrue(self):
        with patch('services.topics_services.insert_query') as mock_insert_query:
            topic_id = 1
            mock_insert_query.return_value = topic_id

            expected = 'Topic created successfully'
            result = topics.create_new_topic(topic=TopicCreate(title=TITLE, category_id=CATEGORY_ID), user_id=USER_ID)

            self.assertEqual(expected, result)

    
    def test_updateBestReply_updatesBestReplyId_returns_Message(self):
        best_reply_id = 1
        expected = f"Best reply for topic {TOPIC_ID} updated to {best_reply_id}"

        with patch('services.topics_services.update_query') as mock_update_query:
            result = topics.update_best_reply_for_topic(TOPIC_ID, best_reply_id)
            
            mock_update_query.assert_called_once_with(
                '''UPDATE topics SET best_reply_id = ? WHERE topic_id = ?''',
                (best_reply_id, TOPIC_ID)
            )
            
            self.assertEqual(expected, result)
            