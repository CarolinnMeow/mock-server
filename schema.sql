
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    balance REAL NOT NULL DEFAULT 0.0,
    currency TEXT NOT NULL CHECK(currency IN ('RUB', 'USD', 'EUR')),
    type TEXT NOT NULL CHECK(type IN ('physical_entity', 'legal_entity')),
    status TEXT NOT NULL CHECK(status IN ('active', 'blocked', 'closed')),
    owner TEXT,
    company TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'COMPLETED', 'REJECTED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount REAL NOT NULL CHECK(amount > 0),
    currency TEXT NOT NULL CHECK(currency IN ('RUB', 'USD', 'EUR')),
    recipient TEXT NOT NULL,
    account_id TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS consents (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('physical_entity', 'legal_entity')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'REVOKED', 'EXPIRED')),
    tpp_id TEXT NOT NULL,
    permissions TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS vrps (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'PAUSED', 'CANCELLED')),
    max_amount REAL NOT NULL CHECK(max_amount > 0),
    frequency TEXT NOT NULL CHECK(frequency IN ('DAILY', 'WEEKLY', 'MONTHLY')),
    valid_until DATE NOT NULL,
    recipient_account TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_account) REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS medical_insured (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    policy_number TEXT NOT NULL UNIQUE,
    birth_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS bank_docs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('STATEMENT', 'CONTRACT', 'CERTIFICATE')),
    content TEXT NOT NULL,
    signature TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    account_id TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS insurance_docs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('POLICY', 'CLAIM', 'AGREEMENT')),
    content TEXT NOT NULL,
    policy_number TEXT NOT NULL,
    valid_until DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_agreements (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACTIVE', 'REJECTED')),
    product_type TEXT NOT NULL CHECK(product_type IN ('LOAN', 'DEPOSIT', 'INSURANCE')),
    terms TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    description TEXT,
    account_id TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
);


CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(type);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_vrp_recipient ON vrps(recipient_account);
