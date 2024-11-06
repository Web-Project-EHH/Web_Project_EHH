
import unittest
from unittest.mock import patch
from data.models.user import User, UserResponse
from services.users_services import create_user, get_user, get_users


       

class TestUserServices(unittest.TestCase):

    @patch('services.users_services.insert_query')
    def test_create_user(self, mock_insert_query):
        user = User(username='testuser', password='password', email='test@example.com', first_name='Test', last_name='User')
        mock_insert_query.return_value = 1
        user_id = create_user(user)
        self.assertEqual(user_id, 1)
        mock_insert_query.assert_called_once_with(
            'INSERT INTO users (username, password, email, first_name, last_name) VALUES (?, ?, ?, ?, ?)',
            ('testuser', 'password', 'test@example.com', 'Test', 'User')
        )

    @patch('services.users_services.read_query')
    def test_get_user(self, mock_read_query):
        mock_read_query.return_value = [(1,'testuser', 'hashed_password', 'test@example.com', 'Test', 'User', False)]
        user_response = get_user('testuser')
        self.assertIsInstance(user_response, UserResponse)
        self.assertEqual(user_response.username, 'testuser')
        self.assertFalse(user_response.is_admin)
        mock_read_query.assert_called_once_with('SELECT * FROM users WHERE username=?', ('testuser',))

    @patch('services.users_services.read_query')
    def test_get_user_not_found(self, mock_read_query):
        mock_read_query.return_value = []
        user_response = get_user('testuser')
        self.assertIsNone(user_response)
        mock_read_query.assert_called_once_with('SELECT * FROM users WHERE username=?', ('testuser',))


    @patch('services.users_services.read_query')
    def test_get_users(self, mock_read_query):
        mock_read_query.return_value = [
            (1, 'testuser1', 'hashed_password', 'test1@example.com', 'Test1', 'User1', False),
            (2, 'testuser2', 'hashed_password', 'test2@example.com', 'Test2', 'User2', False)
            ]
        users = get_users()  
        self.assertIsInstance(users[0], UserResponse)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].username, 'testuser1')
        self.assertEqual(users[1].username, 'testuser2')
        mock_read_query.assert_called_once_with('SELECT * FROM users')     