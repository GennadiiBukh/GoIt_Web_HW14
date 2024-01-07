import unittest
from unittest.mock import Mock
from src.repository.users import get_user_by_email, register_user, confirm_email
from src.database.models import User

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.db_session_mock = Mock()

    def test_get_user_by_email_found(self):
        # Підготовка тестових даних
        email = 'user@example.com'
        expected_user = User(email=email)

        # Налаштування моку
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = expected_user

        # Виклик тестуємої функції
        result = get_user_by_email(self.db_session_mock, email)

        # Перевірка результату
        # self.db_session_mock.query.assert_called_once()
        # self.db_session_mock.query.return_value.filter.return_value.first.assert_called_once()
        # self.assertEqual(result, expected_user)

        self.db_session_mock.query.assert_called_once()
        filter_call_args = self.db_session_mock.query.return_value.filter.call_args_list
        self.assertEqual(str(filter_call_args[0][0][0].left), "users.email")
        self.assertEqual(str(filter_call_args[0][0][0].right.value), email)
        self.assertEqual(result, expected_user)

    def test_get_user_by_email_not_found(self):
        email = 'nonexistent@example.com'

        self.db_session_mock.query.return_value.filter.return_value.first.return_value = None

        result = get_user_by_email(self.db_session_mock, email)

        self.db_session_mock.query.assert_called_once()
        filter_call_args = self.db_session_mock.query.return_value.filter.call_args_list
        self.assertEqual(str(filter_call_args[0][0][0].left), "users.email")
        self.assertEqual(str(filter_call_args[0][0][0].right.value), email)
        self.assertIsNone(result)

    def test_register_user(self):
        # Підготовка тестових даних
        username = 'newuser'
        email = 'newuser@example.com'
        hashed_password = 'hashedpassword'

        # Виклик тестуємої функції
        result = register_user(self.db_session_mock, username, email, hashed_password)

        # Перевірка результату
        self.assertIsNotNone(result)
        self.assertEqual(result.email, email)
        self.db_session_mock.add.assert_called_once()
        self.db_session_mock.commit.assert_called_once()
        self.db_session_mock.refresh.assert_called_once()

    def test_confirm_email(self):
        # Підготовка тестових даних
        email = 'user@example.com'
        user_to_confirm = User(email=email)

        # Налаштування моку
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = user_to_confirm

        # Виклик тестуємої функції
        confirm_email(self.db_session_mock, email)

        # Перевірка результату
        self.db_session_mock.query.assert_called_once()
        self.assertTrue(user_to_confirm.confirmed)
        self.db_session_mock.commit.assert_called_once()

    def tearDown(self):
        self.db_session_mock.reset_mock()


if __name__ == '__main__':
    unittest.main()
