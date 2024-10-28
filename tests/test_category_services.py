from datetime import datetime
from unittest import TestCase
from data.models.category import Category, CategoryResponse
from test_models import mock_user
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