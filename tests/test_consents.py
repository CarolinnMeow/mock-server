import os
import sqlite3
import unittest
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig

class TestConsents(unittest.TestCase):

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

    def test_create_physical_consent(self):
        data = {
            "tpp_id": "tpp1",
            "permissions": ["read", "write"],
            "subject": "user1",
            "scope": "all"
        }
        response = self.client.post('/consent-pe-v2.0.0/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["type"], "physical_entity")
        self.assertEqual(resp_json["status"], "ACTIVE")
        self.assertEqual(resp_json["tpp_id"], "tpp1")
        self.assertIn("permissions", resp_json)

    def test_create_legal_consent(self):
        data = {
            "tpp_id": "tpp2",
            "permissions": ["read"],
            "subject": "user1",
            "scope": "all"
        }
        response = self.client.post('/consent-le-v2.0.0/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["type"], "legal_entity")
        self.assertEqual(resp_json["tpp_id"], "tpp2")

if __name__ == '__main__':
    unittest.main()
