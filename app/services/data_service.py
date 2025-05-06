from faker import Faker
import base64
from datetime import datetime

fake = Faker('ru_RU')

class DataService:
    def __init__(self):
        self.data = {
            "accounts": [],
            "payments": [],
            "consents": {},
            "bank_docs": {},
            "insurance_docs": {},
            "vrp": [],
            "transactions": [],
            "medical_insured": [],
            "product_agreements": []
        }
        self._generate_test_data()

    def _generate_test_data(self):
        for _ in range(5):
            self.data['accounts'].append({
                "id": f"PE{fake.random_number(6)}",
                "balance": fake.pyfloat(positive=True, min_value=1000, max_value=1000000),
                "currency": "RUB",
                "type": "physical_entity",
                "status": "active",
                "owner": fake.name()
            })
            self.data['accounts'].append({
                "id": f"LE{fake.random_number(6)}",
                "balance": fake.pyfloat(positive=True, min_value=5000, max_value=5000000),
                "currency": "USD",
                "type": "legal_entity",
                "status": "active",
                "company": fake.company()
            })
        for _ in range(20):
            account = fake.random_element(elements=[acc for acc in self.data['accounts']])
            self.data['transactions'].append({
                "id": f"TX{fake.random_number(8)}",
                "date": fake.date_time_this_year().isoformat(),
                "amount": fake.pyfloat(min_value=-100000, max_value=100000),
                "description": fake.catch_phrase(),
                "account_id": account['id'],
                "status": fake.random_element(elements=["completed", "pending", "reversed"])
            })
        for _ in range(5):
            self.data['vrp'].append({
                "id": f"VRP{fake.random_number(6)}",
                "max_amount": fake.pyfloat(min_value=1000, max_value=50000),
                "frequency": fake.random_element(elements=["DAILY", "WEEKLY", "MONTHLY"]),
                "valid_until": fake.future_date(end_date='+5y').isoformat(),
                "status": "ACTIVE"
            })
        for _ in range(5):
            self.data['medical_insured'].append({
                "id": f"MED{fake.random_number(6)}",
                "name": fake.name(),
                "policy_number": f"POL{fake.random_number(9)}",
                "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
            })
        for _ in range(5):
            doc_id = f"DOC{fake.random_number(6)}"
            self.data['bank_docs'][doc_id] = {
                "id": doc_id,
                "type": "statement",
                "content": base64.b64encode(fake.text().encode()).decode(),
                "signature": fake.sha256(),
                "created_at": fake.date_time_this_year().isoformat()
            }
        for _ in range(5):
            doc_id = f"INS{fake.random_number(6)}"
            self.data['insurance_docs'][doc_id] = {
                "id": doc_id,
                "type": "policy",
                "content": base64.b64encode(fake.text().encode()).decode(),
                "policy_number": f"POL{fake.random_number(9)}",
                "valid_until": fake.future_date(end_date='+3y').isoformat()
            }

    # Методы для всех сущностей (пример для accounts, payments, consents, и т.д.)
    def get_accounts(self, acc_type):
        return [acc for acc in self.data['accounts'] if acc['type'] == acc_type]

    def get_account(self, account_id, acc_type):
        return next((a for a in self.data['accounts'] if a['id'] == account_id and a['type'] == acc_type), None)

    def add_account(self, account_data, acc_type):
        new_account = {
            "id": f"{'PE' if acc_type == 'physical_entity' else 'LE'}{fake.random_number(6)}",
            "balance": account_data.get("balance", 0.0),
            "currency": account_data.get("currency", "RUB" if acc_type == "physical_entity" else "USD"),
            "type": acc_type,
            "status": "active"
        }
        self.data['accounts'].append(new_account)
        return new_account

    def delete_account(self, account_id, acc_type):
        account = self.get_account(account_id, acc_type)
        if account:
            self.data['accounts'].remove(account)

    def add_payment(self, payment):
        self.data['payments'].append(payment)

    def get_payment(self, payment_id):
        return next((p for p in self.data['payments'] if p['id'] == payment_id), None)

    def delete_payment(self, payment_id):
        payment = self.get_payment(payment_id)
        if payment:
            self.data['payments'].remove(payment)

    def get_payments(self):
        return self.data['payments']

    def add_consent(self, consent):
        self.data['consents'][consent['id']] = consent

    def get_consent(self, consent_id, consent_type):
        consent = self.data['consents'].get(consent_id)
        if consent and consent['type'] == consent_type:
            return consent
        return None

    def delete_consent(self, consent_id):
        if consent_id in self.data['consents']:
            del self.data['consents'][consent_id]

    def add_bank_doc(self, doc_data):
        doc_id = f"DOC{fake.random_number(6)}"
        doc = {
            "id": doc_id,
            "type": "statement",
            "content": doc_data.get("content", "base64content"),
            **doc_data
        }
        self.data['bank_docs'][doc_id] = doc
        return doc

    def get_bank_docs(self):
        return self.data['bank_docs'].values()

    def get_bank_doc(self, doc_id):
        return self.data['bank_docs'].get(doc_id)

    def delete_bank_doc(self, doc_id):
        if doc_id in self.data['bank_docs']:
            del self.data['bank_docs'][doc_id]

    def add_insurance_doc(self, doc_data):
        doc_id = f"INS{fake.random_number(6)}"
        doc = {
            "id": doc_id,
            "type": "policy",
            "content": doc_data.get("content", "base64content"),
            **doc_data
        }
        self.data['insurance_docs'][doc_id] = doc
        return doc

    def get_insurance_docs(self):
        return self.data['insurance_docs'].values()

    def get_insurance_doc(self, doc_id):
        return self.data['insurance_docs'].get(doc_id)

    def delete_insurance_doc(self, doc_id):
        if doc_id in self.data['insurance_docs']:
            del self.data['insurance_docs'][doc_id]

    def add_vrp(self, vrp):
        self.data['vrp'].append(vrp)

    def get_vrps(self):
        return self.data['vrp']

    def get_vrp(self, vrp_id):
        return next((v for v in self.data['vrp'] if v['id'] == vrp_id), None)

    def delete_vrp(self, vrp_id):
        vrp = self.get_vrp(vrp_id)
        if vrp:
            self.data['vrp'].remove(vrp)

    def get_transactions(self):
        return self.data['transactions']

    def get_transaction(self, tx_id):
        return next((t for t in self.data['transactions'] if t['id'] == tx_id), None)

    def add_medical_insured(self, person):
        self.data['medical_insured'].append(person)

    def get_medical_insured(self):
        return self.data['medical_insured']

    def get_medical_insured_by_id(self, person_id):
        return next((p for p in self.data['medical_insured'] if p['id'] == person_id), None)

    def delete_medical_insured(self, person_id):
        person = self.get_medical_insured_by_id(person_id)
        if person:
            self.data['medical_insured'].remove(person)

    def add_product_agreement(self, agreement):
        self.data['product_agreements'].append(agreement)

    def get_product_agreements(self):
        return self.data['product_agreements']

    def get_product_agreement(self, agreement_id):
        return next((a for a in self.data['product_agreements'] if a['id'] == agreement_id), None)

    def delete_product_agreement(self, agreement_id):
        agreement = self.get_product_agreement(agreement_id)
        if agreement:
            self.data['product_agreements'].remove(agreement)

data_service = DataService()
