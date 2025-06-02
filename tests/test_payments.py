import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db, get_db


class TestPayments(unittest.TestCase):

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

    def test_create_payment(self):
        """Тест создания платежа с валидными данными"""
        # Получаем тестовый аккаунт
        with self.app.app_context():
            response = self.client.get('/accounts-v1.3.3/')
            accounts = response.get_json()
            self.assertGreater(len(accounts), 0, "Нет тестовых счетов")
            account_id = accounts[0]["id"]

        test_data = {
            "amount": 100,
            "currency": "RUB",
            "recipient": "Иван Иванов",
            "account_id": account_id
        }

        # Отправка запроса
        response = self.client.post('/payments-v1.3.1/', json=test_data)
        self.assertEqual(response.status_code, 201)

        # Проверка ответа
        payment = response.get_json()
        self.assertEqual(payment["amount"], test_data["amount"])
        self.assertEqual(payment["currency"], test_data["currency"])
        self.assertEqual(payment["recipient"], test_data["recipient"])
        self.assertEqual(payment["account_id"], account_id)
        self.assertEqual(payment["status"], "PENDING")
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
            self.assertEqual(db_payment["amount"], test_data["amount"])

    def test_create_payment_missing_required_field(self):
        """Тест создания платежа с отсутствующим обязательным полем"""
        invalid_data = {
            "amount": 100,
            "currency": "RUB",
            # Пропущено поле recipient
            "account_id": "test-acc-1"
        }
        response = self.client.post('/payments-v1.3.1/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("validation_error", error["error"])

    def test_create_payment_invalid_account(self):
        """Тест создания платежа с несуществующим счетом"""
        invalid_data = {
            "amount": 100,
            "currency": "RUB",
            "recipient": "Иван Иванов",
            "account_id": "invalid_account_id"
        }
        response = self.client.post('/payments-v1.3.1/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("error", error)


if __name__ == '__main__':
    unittest.main()
