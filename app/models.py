from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, UniqueConstraint

from app.extensions import db


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("type", "name", name="uq_categories_type_name"),
        CheckConstraint("type IN ('income', 'expense')", name="ck_categories_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="ck_transactions_type"),
        CheckConstraint("amount >= 0", name="ck_transactions_amount_nonnegative"),
        db.Index("idx_transactions_date", "occurred_on"),
        db.Index("idx_transactions_type_category", "type", "category_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    occurred_on = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    category = db.relationship("Category", backref=db.backref("transactions", lazy=True))


class MonthlyBudget(db.Model):
    __tablename__ = "monthly_budgets"
    __table_args__ = (
        db.UniqueConstraint("month", name="uq_monthly_budgets_month"),
        CheckConstraint("total_amount >= 0", name="ck_monthly_budgets_nonnegative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
