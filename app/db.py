import sqlite3
import click
from flask import current_app, g, abort
import uuid
import json
from app.config import (
    TEST_ACCOUNTS,
    TEST_CONSENTS,
    TEST_PAYMENTS,
    TEST_BANK_DOCS,
    TEST_INSURANCE_DOCS,
    TEST_PRODUCT_AGREEMENTS,
    TEST_VRPS,
    TEST_TRANSACTIONS,
    TEST_MEDICAL_INSURED,
    ACCOUNT_TYPES,
    CONSENT_TYPES,
    PAYMENT_STATUSES,
    PAYMENT_TYPES,
    AGREEMENT_STATUSES,
    VRP_STATUSES
)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def execute_query(query, args=(), commit=False):
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    return cur

def init_db(db=None, db_path=None, fill_test_data=False):
    close = False
    if db is None:
        if db_path is not None:
            db = sqlite3.connect(db_path)
            close = True
        else:
            db = sqlite3.connect(current_app.config['DATABASE'])
            close = True
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
    except FileNotFoundError:
        print("Ошибка: файл schema.sql не найден в корне проекта!")
        exit(1)
    finally:
        if close:
            db.close()

    if fill_test_data:
        # Наполняем данными через отдельное соединение в контексте приложения
        fill_test_db()

def safe_db_query(query, params=(), commit=False):
    import logging
    logger = logging.getLogger(__name__)
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"DB error: {e}")
        abort(500, description="Database error")

@click.command('init-db')
@click.option('--test-data', is_flag=True, help='Fill database with test data')
def init_db_command(test_data):
    init_db(fill_test_data=test_data)
    click.echo(f'База данных инициализирована.{" Тестовые данные добавлены." if test_data else ""}')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def fill_test_db():
    # Accounts (physical)
    for acc in TEST_ACCOUNTS.get("physical", []):
        execute_query(
            '''INSERT INTO accounts (id, balance, currency, type, status, owner)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                str(uuid.uuid4()),
                acc["balance"],
                acc["currency"],
                ACCOUNT_TYPES["physical"],
                acc["status"],
                acc["owner"]
            ),
            commit=True
        )
    # Accounts (legal)
    for acc in TEST_ACCOUNTS.get("legal", []):
        execute_query(
            '''INSERT INTO accounts (id, balance, currency, type, status, company)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                str(uuid.uuid4()),
                acc["balance"],
                acc["currency"],
                ACCOUNT_TYPES["legal"],
                acc["status"],
                acc["company"]
            ),
            commit=True
        )

    # Consents
    for c in TEST_CONSENTS:
        execute_query(
            '''INSERT INTO consents (id, type, status, tpp_id, permissions, account_id)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                str(uuid.uuid4()),
                c["type"],
                c["status"],
                c["tpp_id"],
                json.dumps(c["permissions"]),
                c["account_id"]
            ),
            commit=True
        )

    # Payments
    for p in TEST_PAYMENTS:
        execute_query(
            '''INSERT INTO payments (id, status, type, amount, currency, recipient, created_at, account_id)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)''',
            (
                str(uuid.uuid4()),
                PAYMENT_STATUSES["pending"],
                PAYMENT_TYPES["standard"],
                p["amount"],
                p["currency"],
                p["recipient"],
                p["account_id"]
            ),
            commit=True
        )

    # Bank documents
    for d in TEST_BANK_DOCS:
        execute_query(
            '''INSERT INTO bank_docs (id, type, content, signature, created_at, account_id)
               VALUES (?, ?, ?, ?, datetime('now'), ?)''',
            (
                str(uuid.uuid4()),
                d["type"],
                d["content"],
                d["signature"],
                d["account_id"]
            ),
            commit=True
        )

    # Insurance documents
    for d in TEST_INSURANCE_DOCS:
        execute_query(
            '''INSERT INTO insurance_docs (id, type, content, policy_number, valid_until, created_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))''',
            (
                str(uuid.uuid4()),
                d["type"],
                d["content"],
                d["policy_number"],
                d["valid_until"]
            ),
            commit=True
        )

    # Product agreements
    for a in TEST_PRODUCT_AGREEMENTS:
        execute_query(
            '''INSERT INTO product_agreements (id, product_type, terms, status, account_id)
               VALUES (?, ?, ?, ?, ?)''',
            (
                str(uuid.uuid4()),
                a["product_type"],
                json.dumps(a["terms"]),
                AGREEMENT_STATUSES["active"],
                a["account_id"]
            ),
            commit=True
        )

    # VRPs
    for v in TEST_VRPS:
        execute_query(
            '''INSERT INTO vrps (id, status, max_amount, frequency, valid_until, recipient_account)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                str(uuid.uuid4()),
                VRP_STATUSES["active"],
                v["max_amount"],
                v["frequency"],
                v["valid_until"],
                v["recipient_account"]
            ),
            commit=True
        )

    # Transactions
    for t in TEST_TRANSACTIONS:
        execute_query(
            '''INSERT INTO transactions (id, amount, currency, date, account_id, status)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                t["id"],
                t["amount"],
                t["currency"],
                t["date"],
                t["account_id"],
                t["status"]
            ),
            commit=True
        )

    # Medical insured
    for m in TEST_MEDICAL_INSURED:
        execute_query(
            '''INSERT INTO medical_insured (id, name, policy_number, birth_date)
               VALUES (?, ?, ?, ?)''',
            (
                str(uuid.uuid4()),
                m["name"],
                m["policy_number"],
                m["birth_date"]
            ),
            commit=True
        )