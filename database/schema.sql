CREATE DATABASE IF NOT EXISTS sk3017_bookkeeping
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sk3017_bookkeeping;

CREATE TABLE IF NOT EXISTS categories (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  type VARCHAR(10) NOT NULL,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_type_name (type, name),
  KEY idx_categories_type (type),
  CONSTRAINT ck_categories_type CHECK (type IN ('income', 'expense'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS transactions (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  type VARCHAR(10) NOT NULL,
  category_id INT UNSIGNED NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  occurred_on DATE NOT NULL,
  note VARCHAR(255) NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  KEY idx_transactions_date (occurred_on),
  KEY idx_transactions_type_category (type, category_id),
  CONSTRAINT fk_transactions_category
    FOREIGN KEY (category_id) REFERENCES categories (id),
  CONSTRAINT ck_transactions_type CHECK (type IN ('income', 'expense')),
  CONSTRAINT ck_transactions_amount_nonnegative CHECK (amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS monthly_budgets (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  month DATE NOT NULL,
  total_amount DECIMAL(12, 2) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_monthly_budgets_month (month),
  CONSTRAINT ck_monthly_budgets_nonnegative CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
