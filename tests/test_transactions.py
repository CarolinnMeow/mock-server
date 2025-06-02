import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db

class TestTransactions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Инициализация тестовой среды"""
        db_path = TestConfig.DATABASE
        if os.path.exists(db_path):
            os.remove(db_path)
        cls.app = create_app(config_class=TestConfig)
        with cls.app.app_context():
            init_db(fill_test_data=True)
        cls.client = cls.app.test_client()

    def setUp(self):
        self.client = self.app.test_client()

    def test_get_transactions(self):
        response = self.client.get('/transaction-history-v1.0.0/')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("transactions", json_data)
        self.assertIsInstance(json_data["transactions"], list)

        # Проверка структуры транзакции, если есть хотя бы одна
        if json_data["transactions"]:
            tx = json_data["transactions"][0]
            self.assertIn("id", tx)
            self.assertIn("amount", tx)
            self.assertIn("currency", tx)
            self.assertIn("date", tx)
            self.assertIn("account_id", tx)

if __name__ == '__main__':
    unittest.main()
