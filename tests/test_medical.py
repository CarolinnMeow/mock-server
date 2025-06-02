import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db, get_db


class TestMedical(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Инициализация тестового окружения"""
        # Удаляем старую тестовую базу
        db_path = TestConfig.DATABASE
        if os.path.exists(db_path):
            os.remove(db_path)

        # Создаём приложение и инициализируем базу
        cls.app = create_app(config_class=TestConfig)
        with cls.app.app_context():
            init_db(fill_test_data=True)
        cls.client = cls.app.test_client()

    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.client = self.app.test_client()

    def test_create_medical_insured(self):
        test_data = {
            "name": "Иван Иванов",
            "policy_number": "POL123456",
            "birth_date": "1990-01-01"
        }

        # Тестирование создания записи
        response = self.client.post('/medical-insured-person-v3.0.3/', json=test_data)
        self.assertEqual(response.status_code, 201)

        # Проверка содержимого ответа
        resp_json = response.get_json()
        self.assertEqual(resp_json["name"], test_data["name"])
        self.assertEqual(resp_json["policy_number"], test_data["policy_number"])
        self.assertEqual(resp_json["birth_date"], test_data["birth_date"])
        self.assertIn("id", resp_json)

        # Проверка существования в базе данных
        with self.app.app_context():
            db = get_db()
            person = db.execute(
                'SELECT * FROM medical_insured WHERE id = ?',
                (resp_json["id"],)
            ).fetchone()
            self.assertIsNotNone(person)
            self.assertEqual(person["name"], test_data["name"])

    def test_create_invalid_medical_insured(self):
        # Тест с неполными данными
        invalid_data = {
            "name": "Иван Иванов",
            "birth_date": "1990-01-01"
        }

        response = self.client.post('/medical-insured-person-v3.0.3/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("Validation error", error["error"])


if __name__ == '__main__':
    unittest.main()
