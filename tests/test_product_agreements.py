import os
import unittest
from app import create_app
from app.config import TestConfig
from app.db import init_db, get_db

class TestProductAgreements(unittest.TestCase):

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

    def test_create_product_agreement(self):
        data = {
            "product_type": "LOAN",
            "terms": {"rate": 0.15, "duration": 12}
        }
        response = self.client.post('/product-agreement-consents-v1.0.1/', json=data)
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertEqual(resp_json["product_type"], data["product_type"])
        self.assertIn("terms", resp_json)
        self.assertEqual(resp_json["terms"]["rate"], 0.15)
        self.assertEqual(resp_json["terms"]["duration"], 12)
        self.assertIn("id", resp_json)
        self.assertIn("status", resp_json)

        # Проверка сохранения в БД
        with self.app.app_context():
            db = get_db()
            agreement = db.execute(
                'SELECT * FROM product_agreements WHERE id = ?',
                (resp_json["id"],)
            ).fetchone()
            self.assertIsNotNone(agreement)
            self.assertEqual(agreement["product_type"], data["product_type"])

    def test_create_invalid_product_agreement(self):
        # Нет обязательного поля product_type
        invalid_data = {
            "terms": {"rate": 0.15, "duration": 12}
        }
        response = self.client.post('/product-agreement-consents-v1.0.1/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn("validation_error", error["error"])

if __name__ == '__main__':
    unittest.main()
