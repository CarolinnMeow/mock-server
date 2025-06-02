import os
import unittest
from datetime import datetime
from app import create_app
from app.config import TestConfig
from app.db import init_db, get_db


class TestVRP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Инициализация тестовой среды"""
        # Удаление старой тестовой БД
        db_path = TestConfig.DATABASE
        if os.path.exists(db_path):
            os.remove(db_path)

        # Создание приложения и инициализация БД
        cls.app = create_app(config_class=TestConfig)
        with cls.app.app_context():
            init_db(fill_test_data=True)
        cls.client = cls.app.test_client()

    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.client = self.app.test_client()

    def test_create_vrp(self):
        """Тест создания VRP с валидными данными"""
        test_data = {
            "max_amount": 5000,
            "frequency": "MONTHLY",
            "valid_until": "2026-01-01T00:00:00",
            "recipient_account": "RU0012345678"
        }

        response = self.client.post('/vrp-v1.3.1/', json=test_data)
        self.assertEqual(response.status_code, 201)

        # Проверка ответа
        vrp_data = response.get_json()
        self.assertEqual(vrp_data["max_amount"], test_data["max_amount"])
        self.assertEqual(vrp_data["frequency"], test_data["frequency"])
        self.assertEqual(vrp_data["recipient_account"], test_data["recipient_account"])
        self.assertEqual(vrp_data["status"], "ACTIVE")
        self.assertIn("id", vrp_data)
        self.assertIn("created_at", vrp_data)

        # Проверка сохранения в БД
        with self.app.app_context():
            db = get_db()
            vrp = db.execute(
                'SELECT * FROM vrps WHERE id = ?',
                (vrp_data["id"],)
            ).fetchone()
            self.assertIsNotNone(vrp)
            self.assertEqual(vrp["max_amount"], test_data["max_amount"])

    def test_create_vrp_invalid_data(self):
        """Тест создания VRP с невалидными данными"""
        invalid_data = {
            "frequency": "INVALID_FREQ",  # Недопустимое значение
            "max_amount": -100,  # Отрицательная сумма
            "valid_until": "2020-01-01"  # Дата в прошлом
        }

        response = self.client.post('/vrp-v1.3.1/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("validation_error", error["error"])

    def test_get_vrp_list(self):
        """Тест получения списка VRP"""
        response = self.client.get('/vrp-v1.3.1/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("vrps", data)
        self.assertIsInstance(data["vrps"], list)


if __name__ == '__main__':
    unittest.main()
