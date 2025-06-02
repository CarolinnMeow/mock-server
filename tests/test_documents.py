import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db, fill_test_db


class TestDocuments(unittest.TestCase):

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
            init_db(fill_test_data=True)  # Наполняем тестовыми данными
        cls.client = cls.app.test_client()

    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.client = self.app.test_client()

    def test_create_bank_doc(self):
        # Получаем тестовый аккаунт из предзаполненных данных
        with self.app.app_context():
            response = self.client.get('/accounts-v1.3.3/')
            accounts = response.get_json()
            self.assertGreater(len(accounts), 0, "Нет тестовых аккаунтов")
            account_id = accounts[0]["id"]

        test_data = {
            "type": "STATEMENT",
            "content": "dGVzdA==",
            "signature": "sig123",
            "account_id": account_id
        }

        response = self.client.post('/bank-doc-v1.0.1/', json=test_data)
        self.assertEqual(response.status_code, 201)

        # Проверка содержимого ответа
        doc = response.get_json()
        self.assertEqual(doc["type"], test_data["type"])
        self.assertEqual(doc["content"], test_data["content"])
        self.assertEqual(doc["signature"], test_data["signature"])
        self.assertEqual(doc["account_id"], account_id)
        self.assertIn("created_at", doc)

    def test_create_insurance_doc(self):
        test_data = {
            "type": "POLICY",
            "content": "dGVzdA==",
            "policy_number": "P12345",
            "valid_until": "2025-12-31"
        }

        response = self.client.post('/insurance-doc-v1.0.1/', json=test_data)
        self.assertEqual(response.status_code, 201)

        # Подробная проверка ответа
        doc = response.get_json()
        self.assertEqual(doc["type"], test_data["type"])
        self.assertEqual(doc["policy_number"], test_data["policy_number"])
        self.assertEqual(doc["valid_until"], test_data["valid_until"])
        self.assertIn("created_at", doc)

    def test_create_doc_with_invalid_data(self):
        invalid_data = {
            "type": "INVALID_TYPE",
            "content": "invalid"
        }

        response = self.client.post('/bank-doc-v1.0.1/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("validation_error", error["error"])


if __name__ == '__main__':
    unittest.main()
