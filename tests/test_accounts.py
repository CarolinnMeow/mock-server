import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db, fill_test_db


class TestAccounts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Выполняется один раз перед всеми тестами"""
        cls.app = create_app(config_class=TestConfig)
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

        # Удаляем старую тестовую базу
        if os.path.exists(cls.app.config['DATABASE']):
            os.remove(cls.app.config['DATABASE'])

        # Инициализируем базу в контексте приложения
        with cls.app.app_context():
            init_db(fill_test_data=True)  # Добавляем тестовые данные

    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.app = create_app(config_class=TestConfig)
        self.client = self.app.test_client()

    def test_get_physical_accounts(self):
        with self.app.app_context():
            response = self.client.get('/accounts-v1.3.3/')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)  # Проверяем, что данные есть

            # Пример проверки структуры первого элемента
            first_acc = data[0]
            required_fields = {"id", "balance", "currency", "owner", "status", "type"}
            self.assertTrue(required_fields.issubset(first_acc.keys()))

    def test_create_physical_account(self):
        test_data = {
            "balance": 1500,
            "currency": "USD",
            "owner": "Test User",
            "status": "active"
        }

        with self.app.app_context():
            # Проверка успешного создания
            response = self.client.post('/accounts-v1.3.3/', json=test_data)
            self.assertEqual(response.status_code, 201)

            # Проверка содержимого ответа
            created_acc = response.get_json()
            self.assertEqual(created_acc["balance"], test_data["balance"])
            self.assertEqual(created_acc["owner"], test_data["owner"])

            # Проверка существования в базе
            from app.db import get_db
            db = get_db()
            acc = db.execute('SELECT * FROM accounts WHERE id = ?', (created_acc["id"],)).fetchone()
            self.assertIsNotNone(acc)

    def test_create_account_missing_owner(self):
        invalid_data = {
            "balance": 1000,
            "currency": "RUB",
            "status": "active"
        }

        with self.app.app_context():
            response = self.client.post('/accounts-v1.3.3/', json=invalid_data)
            self.assertEqual(response.status_code, 400)
            error_data = response.get_json()
            self.assertIn("Validation error", error_data["error"])



if __name__ == '__main__':
    unittest.main()
