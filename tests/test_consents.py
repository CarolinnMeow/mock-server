import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db

class TestConsents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Удаляем старую тестовую базу
        db_path = TestConfig.DATABASE
        if os.path.exists(db_path):
            os.remove(db_path)
        # Создаём приложение и инициализируем базу с тестовыми данными
        cls.app = create_app(config_class=TestConfig)
        with cls.app.app_context():
            init_db(fill_test_data=True)
        cls.client = cls.app.test_client()

    def setUp(self):
        self.client = self.app.test_client()

    def test_create_physical_consent(self):
        data = {
            "tpp_id": "tpp1",
            "permissions": ["read", "write"]
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
            "permissions": ["read"]
        }
        response = self.client.post('/consent-le-v2.0.0/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["type"], "legal_entity")
        self.assertEqual(resp_json["tpp_id"], "tpp2")

if __name__ == '__main__':
    unittest.main()
