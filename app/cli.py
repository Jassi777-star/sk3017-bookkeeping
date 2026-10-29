import calendar
import random
from datetime import date
from decimal import Decimal

import click

from app.extensions import db
from app.models import Category, Transaction
from app.services.periods import shift_month


DEFAULT_CATEGORIES = {
    "expense": ["餐饮", "交通", "学习", "娱乐", "住房", "医疗", "其他支出"],
    "income": ["工资", "兼职", "理财", "其他收入"],
}


def ensure_default_categories():
    existing = {
        (category.type, category.name)
        for category in Category.query.all()
    }
    for category_type, names in DEFAULT_CATEGORIES.items():
        for name in names:
            if (category_type, name) not in existing:
                db.session.add(Category(name=name, type=category_type))
    db.session.commit()


def seed_demo_data():
    ensure_default_categories()
    if Transaction.query.count():
        return False

    categories = {
        (category.type, category.name): category
        for category in Category.query.all()
    }
    expense_names = ["餐饮", "交通", "学习", "娱乐", "住房"]
    rng = random.Random(20261028)
    today = date.today()

    for month_offset in [-5, -4, -3, -2, 0]:
        month_start = shift_month(today.replace(day=1), month_offset)
        last_day = calendar.monthrange(month_start.year, month_start.month)[1]
        for index in range(10):
            occurred_on = month_start.replace(day=min(2 + index * 2, last_day))
            name = expense_names[index % len(expense_names)]
            db.session.add(
                Transaction(
                    type="expense",
                    category=categories[("expense", name)],
                    amount=Decimal(rng.randint(1200, 9800)) / 100,
                    occurred_on=occurred_on,
                    note=f"{name}演示记录 {index + 1}",
                )
            )
        db.session.add(
            Transaction(
                type="income",
                category=categories[("income", "工资")],
                amount=Decimal("6500.00"),
                occurred_on=month_start.replace(day=min(5, last_day)),
                note="月度工资",
            )
        )
        if month_offset % 2 == 0:
            db.session.add(
                Transaction(
                    type="income",
                    category=categories[("income", "兼职")],
                    amount=Decimal(rng.randint(60000, 95000)) / 100,
                    occurred_on=month_start.replace(day=min(15, last_day)),
                    note="项目兼职收入",
                )
            )
        else:
            db.session.add(
                Transaction(
                    type="income",
                    category=categories[("income", "理财")],
                    amount=Decimal(rng.randint(10000, 25000)) / 100,
                    occurred_on=month_start.replace(day=min(15, last_day)),
                    note="理财收益",
                )
            )

    db.session.commit()
    return True


def register_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Create tables and insert default categories."""
        db.create_all()
        ensure_default_categories()
        click.echo("Database initialized with default categories.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Insert deterministic demo transactions when the database is empty."""
        db.create_all()
        created = seed_demo_data()
        if created:
            click.echo(f"Inserted {Transaction.query.count()} demo transactions.")
        else:
            click.echo("Transactions already exist; demo data was not inserted.")
