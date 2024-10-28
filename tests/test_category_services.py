from datetime import datetime
from unittest import TestCase
from common.exceptions import ConflictException, NotFoundException
from data.models.category import Category, CategoryResponse
from data.models.topic import TopicCategoryResponseAdmin, TopicCategoryResponseUser
from test_models import mock_category, mock_user
from unittest import mock
from data.database import read_query
from unittest.mock import patch
from services import categories_services

DATE = datetime(2024, 10, 28, 10, 30)

class TestCategoryServices(TestCase):
    
    def setUp(self):
        self.testuser1 = mock_user(1, 'john', '12345', 'john@email.com',
                              'john', 'smith', DATE, False, False)
        self.testadmin1 = mock_user(2, 'george', '12345', 'george@email.com',
                              'george', 'jones', DATE, True, False)
        self.testcategory1 = mock_category(1, 'Electronics', False, False)
        self.testcategory2 = mock_category(2, 'Clothes', False, False)

    @patch('services.categories_services.read_query', autospec=True)
    def testGetCategories_NoCategories_ReturnsNone(self, mock_read_query):
        mock_read_query.return_value = []
        result = categories_services.get_categories(current_user=self.testuser1)
        expected = None
        self.assertEqual(result, expected)
        
    @patch('services.categories_services.read_query', autospec=True)
    def testGetCategories_NoMatchingIDs_ReturnsNone(self, mock_read_query):
        mock_read_query.return_value = []
        result = categories_services.get_categories(current_user=self.testuser1, category_id=1)
        expected = None
        self.assertEqual(result, expected)

    @patch('services.categories_services.read_query', autospec=True)
    def testGetCategories_OneMatchingCategory_ReturnsCategoryResponse(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Electronics')]
        result = categories_services.get_categories(current_user=self.testuser1, category_id=1)
        expected = CategoryResponse(id=1, name='Electronics')
        self.assertEqual(result, expected)

    @patch('services.categories_services.read_query', autospec=True)
    def testGetCategories_SeveralMatchingCategories_ReturnsListOfCategoryReponse(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Electronics'), (2, 'Clothes')]
        result = categories_services.get_categories(current_user=self.testadmin1, category_id=1)
        expected = [CategoryResponse(id=1, name='Electronics'), CategoryResponse(id=2, name='Clothes')]
        self.assertEqual(result, expected)

    @patch('services.categories_services.exists', autospec=True)
    def testCreate_CategoryExists_RaisesException(self, mock_exists):
        mock_exists.return_value = True
        with self.assertRaises(ConflictException):
            categories_services.create(self.testcategory1)

    @patch('services.categories_services.insert_query', autospec=True)
    @patch('services.categories_services.exists', autospec=True)
    def testCreate_CategoryExists_ReturnsID(self, mock_exists, mock_insert_query):
        mock_exists.return_value = False
        self.testcategory1.id = None
        mock_insert_query.return_value = 1
        result = categories_services.create(Category(name='Electronics', is_locked=False, is_private=False))
        expected = Category(id=1, name='Electronics', is_locked=False, 
                            is_deleted=False, is_private=False)
        self.assertEqual(result, expected)

    @patch('services.categories_services.read_query', autospec=True)
    def testExists_CategoryExists_ReturnsTrue(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Electronics')]
        result = categories_services.exists(1)
        self.assertTrue(result)

    @patch('services.categories_services.read_query', autospec=True)
    def testExists_CategoryDoesNotExist_ReturnsFalse(self, mock_read_query):
        mock_read_query.return_value = []
        result = categories_services.exists(1)
        self.assertFalse(result)

    @patch('services.categories_services.exists', autospec=True)
    def testDelete_CategoryDoesNotExist_RaisesException(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            categories_services.delete(1)

    @patch('services.categories_services.update_query', autospec=True)
    @patch('services.categories_services.exists', autospec=True)
    def testDelete_CategoryExistsNoTopics_ReturnsResponse(self, mock_exists, mock_update_query):
        mock_exists.return_value = True
        mock_update_query.return_value = 1
        result = categories_services.delete(1)
        excepted = 'only category deleted'
        self.assertEqual(result, excepted)

    @patch('services.categories_services.update_query', autospec=True)
    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.has_topics', autospec=True)
    def testDelete_CategoryExistsWithTopics_ReturnsResponse(self, mock_has_topics, mock_exists, mock_update_query):
        mock_exists.return_value = True
        mock_has_topics.return_value = True
        mock_update_query.return_value = 2
        result = categories_services.delete(1, True)
        excepted = 'everything deleted'
        self.assertEqual(result, excepted)

    @patch('services.categories_services.update_query', autospec=True)
    @patch('services.categories_services.exists', autospec=True)
    def testUpdateName_CategoryDoesNotExist_RaisesException(self, mock_exists, mock_update_query):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            categories_services.update_name(self.testcategory1, self.testcategory2)

    @patch('services.categories_services.update_query', autospec=True)
    @patch('services.categories_services.exists', autospec=True)
    def testUpdateName_SameName_Raisesexception(self, mock_exists, mock_update_query):
        mock_exists.return_value = True
        mock_update_query.return_value = 1
        with self.assertRaises(ConflictException):
            categories_services.update_name(self.testcategory1, self.testcategory2)
        
    @patch('services.categories_services.update_query', autospec=True)
    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.get_id', autospec=True)
    def testUpdateName_CategoryExists_ReturnsCategoryResponse(self, mock_get_id, mock_exists, mock_update_query):
        mock_exists.side_effect = [True, False]
        mock_update_query.return_value = 1
        mock_get_id.return_value = 1
        result = categories_services.update_name(self.testcategory1, self.testcategory2)
        expected = CategoryResponse(id=1, name='Clothes')
        self.assertEqual(result, expected)


    @patch('services.categories_services.has_topics', autospec=True)
    def testHasTopics_CategoryHasTopics_ReturnsTrue(self, mock_has_topics):
        mock_has_topics.return_value = True
        result = categories_services.has_topics(1)
        self.assertTrue(result)

    @patch('services.categories_services.has_topics', autospec=True)
    def testHasTopics_CategoryHasNoTopics_ReturnsFalse(self, mock_has_topics):
        mock_has_topics.return_value = False
        result = categories_services.has_topics(1)
        self.assertFalse(result)

    @patch('services.categories_services.get_name', autospec=True)
    def testGetName_CategoryExists_ReturnsName(self, mock_get_name):
        mock_get_name.return_value = 'Electronics'
        result = categories_services.get_name(1)
        self.assertEqual(result, 'Electronics')
    
    @patch('services.categories_services.get_id', autospec=True)
    def testGetId_CategoryExists_ReturnsID(self, mock_get_id):
        mock_get_id.return_value = 1
        result = categories_services.get_id('Electronics')
        self.assertEqual(result, 1)

    @patch('services.categories_services.exists', autospec=True)
    def testLockUnlock_CategoryDoesNotExist_RaisesException(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            categories_services.lock_unlock(1)

    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.is_locked', autospec=True)
    @patch('services.categories_services.update_query', autospec=True)
    def testLockUnlock_CategoryExists_ReturnsResponse(self, mock_update_query, mock_is_locked, mock_exists):
        mock_exists.return_value = True
        mock_is_locked.return_value = True
        mock_update_query.return_value = 1
        result = categories_services.lock_unlock(1)
        expected = 'unlocked'
        self.assertEqual(result, expected)

    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.is_locked', autospec=True)
    @patch('services.categories_services.update_query', autospec=True)
    def testLockUnlock_CategoryExists_ReturnsResponse(self, mock_update_query, mock_is_locked, mock_exists):
        mock_exists.return_value = True
        mock_is_locked.return_value = False
        mock_update_query.return_value = 1
        result = categories_services.lock_unlock(1)
        expected = 'locked'
        self.assertEqual(result, expected)

    @patch('services.categories_services.read_query', autospec=True)
    def testIsLocked_CategoryIsLocked_ReturnsTrue(self, mock_read_query):
        mock_read_query.return_value = [(True,)]
        result = categories_services.is_locked(1)
        self.assertTrue(result)

    @patch('services.categories_services.read_query', autospec=True)
    def testIsLocked_CategoryIsNotLocked_ReturnsFalse(self, mock_read_query):
        mock_read_query.return_value = [(False,)]
        result = categories_services.is_locked(1)
        self.assertFalse(result)

    @patch('services.categories_services.read_query', autospec=True)
    def testIsPrivate_CategoryIsPrivate_ReturnsTrue(self, mock_read_query):
        mock_read_query.return_value = [(True,)]
        result = categories_services.is_private(1)
        self.assertTrue(result)

    @patch('services.categories_services.read_query', autospec=True)
    def testIsPrivate_CategoryIsNotPrivate_ReturnsFalse(self, mock_read_query):
        mock_read_query.return_value = [(False,)]
        result = categories_services.is_private(1)
        self.assertFalse(result)

    @patch('services.categories_services.exists', autospec=True)
    def testPrivatiseUnprivatise_CategoryDoesNotExist_RaisesException(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            categories_services.privatise_unprivatise(1)

    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.is_private', autospec=True)
    @patch('services.categories_services.update_query', autospec=True)
    def testPrivatiseUnprivatise_CategoryExists_ReturnsResponse(self, mock_update_query, mock_is_private, mock_exists):
        mock_exists.return_value = True
        mock_is_private.return_value = True
        mock_update_query.return_value = 1
        result = categories_services.privatise_unprivatise(1)
        expected = 'made public'
        self.assertEqual(result, expected)

    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.is_private', autospec=True)
    @patch('services.categories_services.update_query', autospec=True)
    def testPrivatiseUnprivatise_CategoryExists_ReturnsResponse(self, mock_update_query, mock_is_private, mock_exists):
        mock_exists.return_value = True
        mock_is_private.return_value = False
        mock_update_query.return_value = 1
        result = categories_services.privatise_unprivatise(1)
        expected = 'made private'
        self.assertEqual(result, expected)

    @patch('services.categories_services.exists', autospec=True)
    def testGetByID_CategoryDoesNotExist_RaisesException(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            categories_services.get_by_id(1, self.testuser1)

    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.read_query', autospec=True)
    def testGetByID_CategoryExists_ReturnsCategoryResponse(self, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.side_effect = [[(1, 'Electronics')], [(1, 'Hello', 1, 1, 1)]]
        result = categories_services.get_by_id(1, self.testuser1)
        expected = {'Category': CategoryResponse(id=1, name='Electronics'),
                    'Topics': [TopicCategoryResponseUser(topic_id=1, title='Hello', user_id=1, best_reply_id=1, category_id=1)]}
        self.assertEqual(result, expected)

    @patch('services.categories_services.exists', autospec=True)
    @patch('services.categories_services.read_query', autospec=True)
    def testGetByID_CategoryExists_ReturnsResponseAdmin(self, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.side_effect = [[(1, 'Electronics', False, False)], [(1, 'Hello', 1, False, 1, 1)]]
        result = categories_services.get_by_id(1, self.testadmin1)
        expected = {'Category': Category(id=1, name='Electronics', is_locked=False, is_private=False),
                    'Topics': [TopicCategoryResponseAdmin(topic_id=1, title='Hello', user_id=1, is_locked=False, best_reply_id=1, category_id=1)]}
        self.assertEqual(result, expected)

    