import unittest
from unittest.mock import Mock, patch, MagicMock

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.repository.contacts import (create_contact, get_contacts, get_contact, update_contact,
                                     delete_contact, search_contacts, get_upcoming_birthdays)
from src.database.models import Contact
from src.schemas import ContactSchema

class TestContacts(unittest.TestCase):
    def setUp(self):
        self.db_session_mock = MagicMock(spec=Session)

    def test_create_contact(self):
        # Підготовка тестових даних
        contact_data = {
            'first_name': 'Ivan',
            'last_name': 'Ivanenko',
            'email': 'ivan@example.com',
            'phone_number': '+380123456789',
            'birthday': '1990-01-01'
        }
        user_id = 1

        # Спроба створення контакту з валідними даними
        try:
            contact_schema = ContactSchema(**contact_data)

            # Сценарій, коли контакт не існує
            self.db_session_mock.query.return_value.filter.return_value.first.return_value = None
            with patch('src.repository.contacts.Contact', autospec=True):
                result = create_contact(self.db_session_mock, contact_schema.model_dump(), user_id)
                self.assertIsNotNone(result)
                self.db_session_mock.add.assert_called_once()
                self.db_session_mock.commit.assert_called_once()
                self.db_session_mock.refresh.assert_called_once()

            # Очищення моків перед наступним сценарієм
            self.db_session_mock.reset_mock()

            # Сценарій, коли контакт вже існує
            self.db_session_mock.query.return_value.filter.return_value.first.return_value = Contact()
            with patch('src.repository.contacts.Contact', autospec=True):
                result = create_contact(self.db_session_mock, contact_schema.model_dump(), user_id)
                self.assertIsNone(result)
                self.db_session_mock.add.assert_not_called()
                self.db_session_mock.commit.assert_not_called()
                self.db_session_mock.refresh.assert_not_called()

        except ValueError as e:
            # Обробка вийнятку, якщо дані не відповідають схемі
            self.fail(f"Contact data validation failed: {e}")

    def test_get_contacts(self):
        # Підготовка тестових даних
        user_id = 1
        skip = 0
        limit = 10

        test_contacts = [
            Contact(id=1, first_name='Ivan', last_name='Ivanenko', email='ivan@example.com',
                    phone_number='+380123456789', birthday='1990-01-01', additional_data='additional data',
                    user_id=user_id),
            Contact(id=2, first_name='Petro', last_name='Petrenko', email='petro@example.com',
                    phone_number='+380987654321', birthday='1995-05-05', additional_data='additional data',
                    user_id=user_id)
        ]

        # Сценарій, коли контакти не існують
        (self.db_session_mock.query.return_value.filter.return_value.offset.return_value.
         limit.return_value.all).return_value = None
        result = get_contacts(self.db_session_mock, user_id, skip, limit)
        self.assertEqual(result, None)

        # Сценарій, коли контакти існують
        (self.db_session_mock.query.return_value.filter.return_value.offset.return_value.
         limit.return_value.all).return_value = test_contacts
        result = get_contacts(self.db_session_mock, user_id, skip, limit)
        self.assertEqual(result, test_contacts)


    def test_get_contact(self):
        # Підготовка тестових даних
        contact_id = 1
        user_id = 1

        test_contact = Contact(id=1, first_name='Ivan', last_name='Ivanenko', email='ivan@example.com',
                               phone_number='+380123456789', birthday='1990-01-01',
                               additional_data='additional data', user_id=user_id)

        # Сценарій, коли контакт не існує
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = None
        result = get_contact(self.db_session_mock, contact_id, user_id)
        self.assertEqual(result, None)

        # Сценарій, коли контакт існує
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = test_contact
        result = get_contact(self.db_session_mock, contact_id, user_id)
        self.assertEqual(result, test_contact)


    def test_update_contact(self):
        # Підготовка тестових даних
        contact_id = 1
        user_id = 1
        contact_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '+1234567890',
            'birthday': '2022-01-01',
            'additional_data': 'additional data'
        }

        test_contact = Contact(id=1, first_name='Ivan', last_name='Ivanenko', email='ivan@example.com',
                               phone_number='+380123456789', birthday='1990-01-01',
                               additional_data='additional data', user_id=user_id)

        # Сценарій, коли контакт не існує
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = None
        result = update_contact(self.db_session_mock, contact_id, user_id, contact_data)
        self.assertIsNone(result)
        self.assertEqual(result, None)
        self.db_session_mock.commit.assert_not_called()

        # Сценарій, коли контакт існує
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = test_contact
        result = update_contact(self.db_session_mock, contact_id, user_id, contact_data)
        self.assertIsNotNone(result)
        self.assertEqual(result, test_contact)
        self.db_session_mock.commit.assert_called_once()

    def test_update_contact_with_db_error(self):
        contact_id = 1
        user_id = 1
        updated_data = {'first_name': 'John', 'last_name': 'Doe'}
        existing_contact = Contact(id=contact_id, user_id=user_id, first_name='Ivan', last_name='Ivanenko')

        self.db_session_mock.query.return_value.filter.return_value.first.return_value = existing_contact
        self.db_session_mock.commit.side_effect = SQLAlchemyError  # Симуляція помилки бази даних

        with self.assertRaises(SQLAlchemyError):
            update_contact(self.db_session_mock, user_id, contact_id, updated_data)

    def test_delete_contact(self):
        # Підготовка тестових даних
        contact_id = 1
        user_id = 1

        test_contact = Contact(id=1, first_name='Ivan', last_name='Ivanenko', email='ivan@example.com',
                               phone_number='+380123456789', birthday='1990-01-01',
                               additional_data='additional data', user_id=user_id)

        # Сценарій, коли контакт не існує
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = None
        result = delete_contact(self.db_session_mock, contact_id, user_id)
        self.assertIsNone(result)
        self.assertEqual(result, None)
        self.db_session_mock.delete.assert_not_called()
        self.db_session_mock.commit.assert_not_called()

        # Сценарій, коли контакт існує
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = test_contact
        result = delete_contact(self.db_session_mock, contact_id, user_id)
        self.assertIsNotNone(result)
        self.assertEqual(result, test_contact)
        self.db_session_mock.delete.assert_called_with(test_contact)
        self.db_session_mock.commit.assert_called_once()

    def test_delete_contact_with_db_error(self):
        contact_id = 1
        user_id = 1
        contact_to_delete = Contact(id=contact_id, user_id=user_id)

        self.db_session_mock.query.return_value.filter.return_value.first.return_value = contact_to_delete
        self.db_session_mock.commit.side_effect = SQLAlchemyError  # Симуляція помилки бази даних

        with self.assertRaises(SQLAlchemyError):
            delete_contact(self.db_session_mock, user_id, contact_id)

    def test_search_contacts(self):
        user_id = 1
        test_contacts = [Contact(id=1, first_name='Ivan', last_name='Ivanenko', email='ivan@example.com',
                                 phone_number='+380123456789', birthday='1990-01-01',
                                 additional_data='additional data', user_id=user_id),
                         Contact(id=2, first_name='John', last_name='Doe', email='john@example.com',
                                 phone_number='+1234567890', birthday='2022-01-01',
                                 additional_data='additional data', user_id=user_id)]

        #Сценарій, коли контакти не існують
        query_mock = self.db_session_mock.query.return_value
        query_mock.filter.return_value = query_mock  # Повертає сам себе при виклику filter
        query_mock.all.return_value = []
        result = search_contacts(self.db_session_mock, user_id, 'test')
        self.assertEqual(result, [])

        # Сценарій, коли контакти існують
        query_mock = self.db_session_mock.query.return_value
        query_mock.filter.return_value = query_mock  # Повертає сам себе при виклику filter
        query_mock.all.return_value = test_contacts
        result = search_contacts(self.db_session_mock, user_id, 'test')
        self.assertEqual(result, test_contacts)


    def test_get_upcoming_birthdays(self):
        user_id = 1
        test_birthdays = [Contact(id=1, first_name='Ivan', birthday='1990-01-01', user_id=user_id)]

        # Сценарій, коли дні народження не існують
        query_mock = self.db_session_mock.query.return_value
        query_mock.filter.return_value = query_mock  # Повертає сам себе при виклику filter
        query_mock.all.return_value = []
        result = get_upcoming_birthdays(self.db_session_mock, user_id)
        self.assertEqual(result, [])

        # Сценарій, коли дні народження існують
        query_mock = self.db_session_mock.query.return_value
        query_mock.filter.return_value = query_mock  # Повертає сам себе при виклику filter
        query_mock.all.return_value = test_birthdays
        result = get_upcoming_birthdays(self.db_session_mock, user_id)
        self.assertEqual(result, test_birthdays)

    def tearDown (self):
        self.db_session_mock.reset_mock()


if __name__ == '__main__':
    unittest.main()
