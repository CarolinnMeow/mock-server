import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db, get_db


class TestPM211FZ(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Инициализация тестового окружения"""
        # Удаление старой тестовой БД
        db_path = TestConfig.DATABASE
        if os.path.exists(db_path):
            os.remove(db_path)

        # Создание приложения и инициализация БД
        cls.app = create_app(config_class=TestConfig)
        with cls.app.app_context():
            init_db(fill_test_data=True)  # Наполняем тестовыми данными
        cls.client = cls.app.test_client()

    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.client = self.app.test_client()

    def test_create_pm_211fz(self):
        """Тест создания платежа по 211-ФЗ с валидными данными"""
        # Получаем тестовый аккаунт
        with self.app.app_context():
            response = self.client.get('/accounts-v1.3.3/')
            accounts = response.get_json()
            self.assertGreater(len(accounts), 0, "Нет тестовых счетов")
            account_id = accounts[0]["id"]

        test_data = {
            "amount": 1000,
            "currency": "RUB",
            "recipient": "budget-acc-1",
            "purpose": "Оплата налогов",
            "budget_code": "18210102010011000110",
            "account_id": account_id
        }

        # Отправка запроса
        response = self.client.post('/pm-211fz-v1.3.1/', json=test_data)
        self.assertEqual(response.status_code, 201)

        # Проверка ответа
        payment = response.get_json()
        self.assertEqual(payment["amount"], test_data["amount"])
        self.assertEqual(payment["currency"], test_data["currency"])
        self.assertEqual(payment["recipient"], test_data["recipient"])
        self.assertEqual(payment["purpose"], test_data["purpose"])
        self.assertEqual(payment["budget_code"], test_data["budget_code"])
        self.assertEqual(payment["account_id"], account_id)
        self.assertEqual(payment["status"], "PENDING")
        self.assertEqual(payment["type"], "pm_211fz")
        self.assertIn("created_at", payment)
        self.assertIn("id", payment)

        # Проверка сохранения в БД
        with self.app.app_context():
            db = get_db()
            db_payment = db.execute(
                'SELECT * FROM payments WHERE id = ?',
                (payment["id"],)
            ).fetchone()
            self.assertIsNotNone(db_payment)
            self.assertEqual(db_payment["budget_code"], test_data["budget_code"])

    def test_create_invalid_pm_211fz(self):
        """Тест создания платежа с невалидными данными"""
        invalid_data = {
            "amount": -100,  # Негативная сумма
            "currency": "RUB",
            "recipient": "budget-acc-1",
            "account_id": "invalid_account"
        }

        response = self.client.post('/pm-211fz-v1.3.1/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("Validation error", error["error"])

    def test_missing_required_field(self):
        """Тест отсутствия обязательного поля"""
        incomplete_data = {
            "currency": "RUB",
            "recipient": "budget-acc-1",
            "budget_code": "18210102010011000110"
        }

        response = self.client.post('/pm-211fz-v1.3.1/', json=incomplete_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("Validation error", error["error"])


if __name__ == '__main__':
    unittest.main()
