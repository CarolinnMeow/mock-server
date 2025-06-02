import os
import sqlite3
import unittest
from app import create_app
from app.services.data_service import DataService
from app.config import TestConfig

class TestMedical(unittest.TestCase):

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

    def test_create_medical_insured(self):
        data = {
            "name": "Иван Иванов",
            "policy_number": "POL123456",
            "birth_date": "1990-01-01"
        }
        response = self.client.post('/medical-insured-person-v3.0.3/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["name"], "Иван Иванов")
        self.assertEqual(resp_json["policy_number"], "POL123456")

if __name__ == '__main__':
    unittest.main()
