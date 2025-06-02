import os
import sqlite3
import unittest
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig

class TestPayments(unittest.TestCase):

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

    def test_create_payment(self):
        # 1. Получить список счетов
        resp = self.client.get('/accounts-v1.3.3/')
        accounts = resp.get_json()
        self.assertTrue(accounts, "Нет ни одного счета в тестовой базе!")
        account_id = accounts[0]["id"]

        # 2. Использовать account_id при создании платежа
        data = {
            "amount": 100,
            "currency": "RUB",
            "recipient": "Иван",
            "account_id": account_id
        }
        response = self.client.post('/payments-v1.3.1/', json=data)
        self.assertEqual(response.status_code, 201)
        payment = response.get_json()
        self.assertEqual(payment["account_id"], account_id)

if __name__ == '__main__':
    unittest.main()
