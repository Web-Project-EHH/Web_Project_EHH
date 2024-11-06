from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch

import pytest
from common.auth import authenticate_user, create_access_token, get_current_admin_user, get_current_user, verify_password, get_password_hash, verify_token, token_blacklist
from common.exceptions import ForbiddenException, UnauthorizedException
from config import ALGORITHM, SECRET_KEY
from jose import jwt
from data.models.user import User, UserResponse



class TestAuth(unittest.TestCase):

    @patch('common.auth.pwd_context')
    def test_verify_password_success(self, mock_pwd_context):
        password = "mysecretpassword"
        hashed_password = get_password_hash(password)
        self.assertTrue(verify_password(password, hashed_password))


    def test_verify_password_failure(self):
        password = "mysecretpassword"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(password)
        self.assertFalse(verify_password(wrong_password, hashed_password))


    @patch('common.auth.pwd_context')
    def test_get_password_hash(self, mock_pwd_context):
        password    = "mysecret"
        hashed_password = get_password_hash(password)
        self.assertNotEqual(password, hashed_password)
        self.assertTrue(hashed_password, password)


    @patch('common.auth.datetime')
    def test_create_access_token(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 11, 4)
        mock_datetime.timedelta = timedelta
        data = {'sub': 'username'}
        expires_delta = timedelta(minutes=10)
        token = create_access_token(data, expires_delta=expires_delta)
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_exp': False})     

        self.assertEqual(data['sub'], decoded_token['sub'])
        self.assertIn('exp', decoded_token)
        self.assertIsInstance(decoded_token['exp'], int)

    @patch('common.auth.jwt.decode')
    def test_verify_token_valid(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {'sub': 'username'}
        token = create_access_token({'sub': 'username'})
        result = verify_token(token)
        self.assertEqual(result['sub'], 'username')

    def test_verify_token_invalid(self):
        token = create_access_token({'sub': 'username'})
        with self.assertRaises(UnauthorizedException):
            verify_token('invalid_token')

    def test_verify_token_revoked(self):
        token = create_access_token({'sub': 'username'})
        token_blacklist.add(token)
        with self.assertRaises(ForbiddenException):
            verify_token(token)


    @patch('common.auth.read_query')
    @patch('common.auth.verify_password')
    def test_authenticate_user_success(self, mock_verify_password, mock_read_query):
        mock_read_query.return_value = [(1, 'testuser', 'hashedpassword', 'test@example.com', 'First', 'Last', False)]
        mock_verify_password.return_value = True
        mock_user_response = MagicMock(spec=UserResponse)
        mock_user_response.from_query_result.return_value = mock_user_response
        
        with patch('data.models.user.UserResponse', mock_user_response):
            result = authenticate_user('testuser', 'password')

        self.assertIsNotNone(result)



    @patch('common.auth.read_query')
    @patch('common.auth.verify_password')
    def test_authenticate_user_invalid_password(self, mock_verify_password, mock_read_query):
        # Mock the database response
        mock_user_data = [('test_user', 'test_email', 'hashed_password')]
        mock_read_query.return_value = mock_user_data
        mock_verify_password.return_value = False

        result = authenticate_user('test_user', 'test_password')

        self.assertIsNone(result)
                          
    @patch('common.auth.read_query')
    def test_authenticate_user_no_user(self, mock_read_query):
        # Mock the database response
        mock_read_query.return_value = []

        result = authenticate_user('test_user', 'test_password')

        self.assertIsNone(result)

    @patch('common.auth.verify_token')
    def test_get_current_user_no_username(self, mock_verify_token):
        mock_verify_token.return_value = {'sub': None}
        with self.assertRaises(UnauthorizedException):
            get_current_user(token='valid_token')   



    @patch("common.auth.get_user")
    @patch("common.auth.verify_token")
    def test_get_current_user(self, mock_verify_token, mock_get_user):
        token = 'valid_token'
        user = UserResponse(id=1, username='testuser', email='test@example.com', first_name='Test', last_name='User', is_admin=False)

        mock_verify_token.return_value = {"sub": "testuser"}
        mock_get_user.return_value = user

        result = get_current_user(token)
        
        self.assertEqual(result, user)
        self.assertEqual(result.username, "testuser")
        mock_verify_token.assert_called_once_with(token)
        mock_get_user.assert_called_once_with("testuser")



    @patch("common.auth.verify_token")
    @patch("common.auth.get_user")
    def test_get_current_user_invalid_token(self, mock_get_user, mock_verify_token):
        token = 'invalid_token'
        mock_verify_token.side_effect = UnauthorizedException("Invalid token")

        with self.assertRaises(UnauthorizedException):
            get_current_user(token)

        mock_verify_token.assert_called_once_with(token)
        mock_get_user.assert_not_called()

    @patch("common.auth.verify_token")
    @patch("common.auth.get_user")
    def test_get_current_user_no_username(self, mock_get_user, mock_verify_token):
        token = 'valid_token'
        mock_verify_token.return_value = {"sub": None}

        with self.assertRaises(UnauthorizedException):
            get_current_user(token)

        mock_verify_token.assert_called_once_with(token)
        mock_get_user.assert_not_called()

    # Test get_current_admin_user
    @patch("common.auth.get_current_user")
    def test_get_current_admin_user(self, mock_get_current_user):
        admin_user = UserResponse(id=2, username='adminuser', email='admin@example.com', first_name='Admin', last_name='User', is_admin=True)

        result = get_current_admin_user(user=admin_user)

        self.assertEqual(result, admin_user)


    @patch("common.auth.get_current_user")
    def test_get_current_admin_user_not_admin(self, mock_get_current_user):
        non_admin_user = UserResponse(id=1, username='testuser', email='test@example.com', first_name='Test', last_name='User', is_admin=False)

        with self.assertRaises(ForbiddenException):
            get_current_admin_user(user=non_admin_user)
