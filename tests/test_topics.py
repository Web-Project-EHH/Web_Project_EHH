from unittest import TestCase
from unittest.mock import Mock, patch
from routers.api import topics as topics_router
from data.models.category import Category
from data.models.topic import TopicResponse
from fastapi import HTTPException


class TestCategory:
    ID = 1
    NAME = 'TestName'
    LOCKED = False
    PRIVATE = False
    VALUES_TUPLE = (ID, NAME, LOCKED, PRIVATE)
    OBJ = Category.from_query_result(*VALUES_TUPLE)
    
class TestTopic:
    ID = 1
    TITLE = 'TestTitle'
    USER_ID = 1
    AUTHOR = 'TestAuthor'
    STATUS = 0
    BEST_REPLY_ID = None 
    CATEGORY_ID = 1
    CATEGORY_NAME = 'Uncategorized'
    PRIVATE = False
    VALUES_TUPLE = (ID, TITLE, USER_ID, AUTHOR, STATUS, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME)
    OBJ = TopicResponse.from_query(*VALUES_TUPLE)


def fake_user():
    user = Mock()
    user.is_admin = False
    return user

def fake_category(is_private: bool = False, is_locked: bool = False):
    category = Mock()
    category.category_id = 1
    category.is_private = is_private
    category.is_locked = is_locked
    return category

def fake_topic(is_private=False):
    """Creates a mock topic object for testing."""
    return {
        "id": 1,  # Replace with a suitable test ID
        "title": "Sample Topic",
        "content": "This is a sample content for the topic.",
        "is_private": is_private,
    }
    
class TopicsRouter_Should(TestCase):
    
    def test_getAllTopics_returnsTopicsList_when_TopicsExist(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username, \
          patch('services.categories_services.exists_by_name') as mock_exists_by_name, \
          patch('services.topics_services.get_all_topics') as mock_get_all_topics:
            
            mock_exists_by_username.return_value = True
            mock_exists_by_name.return_value = True
            mock_get_all_topics.return_value = [TestTopic.OBJ]
                         
            expected_result = [TestTopic.OBJ]
            result = topics_router.get_topics(Mock())
            
            self.assertEqual(expected_result, result)
            
    def test_getAllTopics_returnsEmptyList_when_NoTopics(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username, \
          patch('services.categories_services.exists_by_name') as mock_exists_by_name, \
          patch('services.topics_services.get_all_topics') as mock_get_all_topics:
                
            mock_exists_by_username.return_value = True
            mock_exists_by_name.return_value = True
            mock_get_all_topics.return_value = []
            
            expected_result = []
            result = topics_router.get_topics(Mock())
            
            self.assertEqual(expected_result, result)
            
    def test_getAllTopics_raisesHTTPException_whenUsernameNotExists(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username:
            mock_exists_by_username.return_value = False 
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), username='fake_username')
                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('User not found', ex.exception.detail)

    def test_getAllTopics_raisesHTTPException_whenCategoryNotExists(self):
        with patch('services.categories_services.exists_by_name') as mock_exists_by_name:
            mock_exists_by_name.return_value = False
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_topics(Mock(), category='fake_category')
            self.assertEqual(404, ex.exception.status_code)
            self.assertEqual('Category not found', ex.exception.detail)

    def test_getTopicById_returnsTopic_when_TopicExists_userHasAccess(self):
        with patch('services.topics_services.get_by_id') as mock_topic_by_id, \
          patch('services.categories_services.get_by_id') as mock_category_by_id, \
          patch('services.categories_services.has_access_to_private_category') as mock_access:
              
            mock_topic_by_id.return_value = TestTopic.OBJ
            mock_category_by_id.return_value = TestCategory.OBJ
            mock_access.return_value = True
                         
            expected_result = TestTopic.OBJ
            result = topics_router.get_topic_by_id(TestTopic.ID, Mock(), Mock())
            
            self.assertEqual(expected_result, result)
        
    def test_getTopicById_raisesHTTPException_whenTopicNotExists(self):
        with patch('services.topics_services.get_by_id') as mock_topic_by_id:
            mock_topic_by_id.return_value = None 
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_topic_by_id(TestTopic.ID, Mock(), Mock())
                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('Topic #ID:1 does not exist', ex.exception.detail)

    def test_getTopicById_raisesHTTPException_whenCategoryPrivate_userNoPermission(self):
        # Mock the fetch_topic_by_id service
        with patch('services.topics_services.fetch_topic_by_id') as mock_fetch_topic:
            # Create a fake private topic
            private_topic = fake_topic(is_private=True)
            mock_fetch_topic.return_value = private_topic

            # Mock the fetch_replies_for_topic service (if needed for completeness)
            with patch('services.topics_services.fetch_replies_for_topic') as mock_fetch_replies:
                mock_fetch_replies.return_value = []  # Assuming no replies for simplicity

                # Now, simulate the request and check for the exception
                with self.assertRaises(HTTPException) as ex:
                    topics_router.get_topic_by_id(TestTopic.ID)  # Only pass topic_id

                # Check if the exception raised is the one we expect
                self.assertEqual(401, ex.exception.status_code)
                self.assertEqual('Login to view topics in private categories', ex.exception.detail)


    def test_createTopic_returnsCorrectMsg_whenCategoryExistsAndUserHasAccess(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id, \
            patch('services.topics_services.create_new_topic') as mock_create_new_topic:
        
            mock_category_by_id.return_value = fake_category()
            mock_create_new_topic.return_value = TestTopic.ID
            
            new_topic = topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)
            
            expected = 'Topic created successfully'
            
            result = topics_router.create_topic(new_topic, fake_user())
            
            self.assertEqual(expected, result.detail)

    def test_createTopic_raisesHTTPException_whenCategoryNotExists(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id:
            mock_category_by_id.return_value = None 
            new_topic = topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)
            with self.assertRaises(HTTPException) as ex:
                topics_router.create_topic(new_topic, fake_user())
                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('Category #ID:1 does not exist', ex.exception.detail)

    def test_createTopic_raisesHTTPException_whenCategoryIsLocked(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id:
            category = TestCategory.OBJ
            category.is_locked = True  
            mock_category_by_id.return_value = category
            new_topic = topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)
            with self.assertRaises(HTTPException) as ex:
                topics_router.create_topic(new_topic, fake_user())
                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('Category #ID:1, Name: TestName is locked', ex.exception.detail)

    def test_createTopic_raisesHTTPException_whenCategoryPrivate_userNoPermission(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id, \
          patch('services.categories_services.has_write_access') as mock_write_access:
            
            category = TestCategory.OBJ
            category.is_private = True  
            mock_category_by_id.return_value = category
            mock_write_access.return_value = False
            new_topic = topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)

            with self.assertRaises(HTTPException) as ex:
                topics_router.create_topic(new_topic, fake_user())
                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('You do not have permission to post in this private category', ex.exception.detail)
