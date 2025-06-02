import os
import sqlite3
import unittest
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig

class TestAccounts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Перед запуском всех тестов пересоздаёт тестовую базу и наполняет её схемой и тестовыми данными.
        """
        cls.db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'test_mockserver.db')
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        conn = sqlite3.connect(cls.db_path)
        conn.executescript(schema)
        conn.close()
        ds = DataService()
        ds.save_to_db(cls.db_path)

    def setUp(self):
        self.app = create_app(config_class=TestConfig)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_get_physical_accounts(self):
        """
        Проверка получения списка счетов физических лиц.
        """
        response = self.client.get('/accounts-v1.3.3/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

        if data:
            acc = data[0]
            self.assertIn("id", acc)
            self.assertIn("balance", acc)
            self.assertIn("currency", acc)
            self.assertIn("owner", acc)

    def test_create_physical_account(self):
        """
        Проверка создания счета физического лица.
        """
        data = {
            "balance": 1000,
            "currency": "RUB",
            "owner": "Иван Иванов",
            "status": "active"
        }
        response = self.client.post('/accounts-v1.3.3/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["balance"], 1000)
        self.assertEqual(resp_json["currency"], "RUB")
        self.assertEqual(resp_json["owner"], "Иван Иванов")
        self.assertIn("id", resp_json)
        self.assertIn("status", resp_json)
        self.assertEqual(resp_json["status"], "active")

    def test_create_account_missing_owner(self):
        """
        Проверка валидации: отсутствие обязательного поля owner.
        """
        data = {
            "balance": 1000,
            "currency": "RUB",
            "status": "active"
        }
        response = self.client.post('/accounts-v1.3.3/', json=data)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
