from datetime import datetime
from unittest import TestCase
from common.exceptions import ForbiddenException, NotFoundException
from data.models.reply import Reply, ReplyResponse
from test_models import mock_user, mock_reply
from unittest.mock import patch
from services import replies_services

DATE = datetime(2024, 10, 28, 10, 30)

class TestReplyServices(TestCase):
    
    def setUp(self):
        self.testuser1 = mock_user(1, 'john', '12345', 'john@email.com',
                                   'john', 'smith', DATE, False, False)
        self.testuser2 = mock_user(2, 'adam', '12345', 'adam@email.com',
                                   'adam', 'jones', DATE, False, False)
        self.testadmin1 = mock_user(2, 'george', '12345', 'george@email.com',
                                    'george', 'jones', DATE, True, False)
        self.testreply1 = mock_reply(1, 'This is a reply', 1, 1, DATE, False)
        self.testreply2 = mock_reply(1,'This is another reply', 2, 2, DATE, False)
    
    @patch('services.replies_services.read_query')
    def testGetReplies_NoRepliesFound_ReturnsNone(self, mock_read_query):
        mock_read_query.return_value = []
        result = replies_services.get_replies()
        self.assertIsNone(result)

    @patch('services.replies_services.read_query')
    def testGetReplies_OneReplyFound_ReturnsReply(self, mock_read_query):
        mock_read_query.return_value = [(1, 'This is a reply', 1, 1, DATE, False)]
        result = replies_services.get_replies()
        expected = Reply(id=1, text='This is a reply', user_id=1, topic_id=1, created=DATE, edited=False)
        self.assertEqual(result, expected)

    @patch('services.replies_services.read_query')
    def testGetReplies_MultipleRepliesFound_ReturnsList(self, mock_read_query):
        mock_read_query.return_value = [(1, 'This is a reply', 1, 1, DATE, False),
                                        (2, 'This is another reply', 2, 2, DATE, False)]
        result = replies_services.get_replies()
        expected = [Reply(id=1, text='This is a reply', user_id=1, topic_id=1, created=DATE, edited=False),
                    Reply(id=2, text='This is another reply', user_id=2, topic_id=2, created=DATE, edited=False)]
        self.assertEqual(result, expected)

    @patch('services.replies_services.read_query')
    def testCreate_NoTopic_RaisesException(self, mock_read_query):
        mock_read_query.return_value = []
        with self.assertRaises(NotFoundException):
           replies_services.create(self.testreply1, self.testuser1)

    @patch('services.replies_services.read_query')
    @patch('services.replies_services.insert_query')
    def testCreate_ReturnsReply(self, mock_insert_query, mock_read_query):
        mock_read_query.return_value = [(1,)]
        mock_insert_query.return_value = 1
        reply_instance = Reply(text='This is another reply', user_id=10, topic_id=1, created=DATE, edited=False)
        result = replies_services.create(reply=reply_instance, current_user=self.testuser1)
        expected = Reply(id=1, text='This is another reply', user_id=1, topic_id=1, created=DATE, edited=False)
        self.assertEqual(result, expected)

    @patch('services.replies_services.exists')
    def testEditText_ReplyNotFound_RaisesException(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            replies_services.edit_text(self.testreply1, self.testreply2, self.testuser1)

    @patch('services.replies_services.exists')
    @patch('services.replies_services.read_query')
    def testEditText_WrongUser_ReturnsReply(self, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.return_value = [('Paul',)]
        with self.assertRaises(ForbiddenException):
            replies_services.edit_text(self.testreply1, self.testreply2, self.testuser2)

    @patch('services.replies_services.exists')
    @patch('services.replies_services.read_query')
    def testEditText_ReturnsReply(self, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.return_value = [('john',)]
        reply_instance = Reply(text='New Text', user_id=1, topic_id=1, created=DATE, edited=False)
        result = replies_services.edit_text(self.testreply1, reply_instance, self.testuser1)
        expected = ReplyResponse(id=1, text='New Text')
        self.assertEqual(result, expected)

    @patch('services.replies_services.read_query')
    def testExists_ReplyNotFound_ReturnsFalse(self, mock_read_query):
        mock_read_query.return_value = []
        result = replies_services.exists(1)
        self.assertFalse(result)

    @patch('services.replies_services.read_query')
    def testExists_ReplyFound_ReturnsTrue(self, mock_read_query):
        mock_read_query.return_value = [(1,)]
        result = replies_services.exists(1)
        self.assertTrue(result)

    @patch('services.replies_services.exists')
    def testDelete_ReplyNotFound_RaisesException(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(NotFoundException):
            replies_services.delete(1, self.testuser1)

    @patch('services.replies_services.exists')
    @patch('services.replies_services.read_query')
    def testDelete_WrongUser_RaisesException(self, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.return_value = [('Paul',)]
        with self.assertRaises(ForbiddenException):
            replies_services.delete(1, self.testuser2)

    @patch('services.replies_services.exists')
    @patch('services.replies_services.read_query')
    @patch('services.replies_services.update_query')
    def testDelete_ReturnsDeleted(self, mock_update_query, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.return_value = [('john',)]
        mock_update_query.return_value = 1
        result = replies_services.delete(1, self.testuser1)
        self.assertEqual(result, 'reply deleted')

    @patch('services.replies_services.exists')
    @patch('services.replies_services.read_query')
    @patch('services.replies_services.update_query')
    def testDelete_Admin_ReturnsDeleted(self, mock_update_query, mock_read_query, mock_exists):
        mock_exists.return_value = True
        mock_read_query.return_value = [('john',)]
        mock_update_query.return_value = 1
        result = replies_services.delete(1, self.testadmin1)
        self.assertEqual(result, 'reply deleted')

    @patch('services.replies_services.read_query')
    def testFetchText_ReturnsText(self, mock_read_query):
        mock_read_query.return_value = [('This is a reply',)]
        result = replies_services.fetch_text(1)
        self.assertEqual(result, 'This is a reply')