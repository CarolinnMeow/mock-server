import os
import sqlite3
import unittest
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig

class TestVRP(unittest.TestCase):

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

    def test_create_vrp(self):
        data = {
            "max_amount": 5000,
            "frequency": "MONTHLY",
            "valid_until": "2026-01-01",
            "recipient_account": "RU0012345678"
        }
        response = self.client.post('/vrp-v1.3.1/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["max_amount"], 5000)
        self.assertEqual(resp_json["frequency"], "MONTHLY")

if __name__ == '__main__':
    unittest.main()
