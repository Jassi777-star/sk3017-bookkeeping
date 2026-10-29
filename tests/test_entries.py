from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Category, Transaction


@pytest.fixture()
def expense_category(app):
    with app.app_context():
        category = Category(name="餐饮", type="expense")
        db.session.add(category)
        db.session.commit()
        return category.id


def test_can_create_expense_transaction(app, client, expense_category):
    response = client.post(
        "/entries/new",
        data={
            "type": "expense",
            "category_id": str(expense_category),
            "amount": "28.50",
            "occurred_on": "2026-10-28",
            "note": "午餐",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        transaction = Transaction.query.one()
        assert transaction.amount == Decimal("28.50")
        assert transaction.note == "午餐"


def test_rejects_negative_amount(app, client, expense_category):
    response = client.post(
        "/entries/new",
        data={
            "type": "expense",
            "category_id": str(expense_category),
            "amount": "-1.00",
            "occurred_on": "2026-10-28",
            "note": "",
        },
    )

    assert response.status_code == 200
    assert "金额必须为非负数".encode() in response.data
    with app.app_context():
        assert Transaction.query.count() == 0


def test_rejects_invalid_date_and_more_than_two_decimals(app, client, expense_category):
    invalid_date = client.post(
        "/entries/new",
        data={
            "type": "expense",
            "category_id": str(expense_category),
            "amount": "12.50",
            "occurred_on": "2026-02-30",
            "note": "",
        },
    )
    invalid_amount = client.post(
        "/entries/new",
        data={
            "type": "expense",
            "category_id": str(expense_category),
            "amount": "12.345",
            "occurred_on": "2026-10-28",
            "note": "",
        },
    )

    assert invalid_date.status_code == 200
    assert "日期格式应为 YYYY-MM-DD".encode() in invalid_date.data
    assert invalid_amount.status_code == 200
    assert "最多保留两位小数".encode() in invalid_amount.data
    with app.app_context():
        assert Transaction.query.count() == 0


def test_rejects_category_with_wrong_type(app, client, expense_category):
    response = client.post(
        "/entries/new",
        data={
            "type": "income",
            "category_id": str(expense_category),
            "amount": "100.00",
            "occurred_on": "2026-10-28",
            "note": "",
        },
    )

    assert response.status_code == 200
    assert "分类与收支类型不一致".encode() in response.data
    with app.app_context():
        assert Transaction.query.count() == 0


def test_can_edit_transaction(app, client, expense_category):
    with app.app_context():
        transaction = Transaction(
            type="expense",
            category_id=expense_category,
            amount=Decimal("18.00"),
            occurred_on=date(2026, 10, 27),
            note="旧备注",
        )
        db.session.add(transaction)
        db.session.commit()
        transaction_id = transaction.id
        created_at = transaction.created_at

    response = client.post(
        f"/entries/{transaction_id}/edit",
        data={
            "type": "expense",
            "category_id": str(expense_category),
            "amount": "25.00",
            "occurred_on": "2026-10-28",
            "note": "新备注",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        transaction = db.session.get(Transaction, transaction_id)
        assert transaction.amount == Decimal("25.00")
        assert transaction.note == "新备注"
        assert transaction.created_at == created_at


def test_delete_requires_post(app, client, expense_category):
    with app.app_context():
        transaction = Transaction(
            type="expense",
            category_id=expense_category,
            amount=Decimal("10.00"),
            occurred_on=date(2026, 10, 27),
        )
        db.session.add(transaction)
        db.session.commit()
        transaction_id = transaction.id

    assert client.get(f"/entries/{transaction_id}/delete").status_code == 405
    assert client.post(f"/entries/{transaction_id}/delete").status_code == 302
    with app.app_context():
        assert db.session.get(Transaction, transaction_id) is None


def test_filters_entries_by_month_type_and_category(app, client):
    with app.app_context():
        food = Category(name="餐饮", type="expense")
        salary = Category(name="工资", type="income")
        db.session.add_all([food, salary])
        db.session.commit()
        db.session.add_all(
            [
                Transaction(
                    type="expense",
                    category_id=food.id,
                    amount=Decimal("20.00"),
                    occurred_on=date(2026, 10, 5),
                    note="目标午餐",
                ),
                Transaction(
                    type="expense",
                    category_id=food.id,
                    amount=Decimal("30.00"),
                    occurred_on=date(2026, 9, 5),
                    note="上月午餐",
                ),
                Transaction(
                    type="income",
                    category_id=salary.id,
                    amount=Decimal("5000.00"),
                    occurred_on=date(2026, 10, 1),
                    note="目标工资",
                ),
            ]
        )
        db.session.commit()
        category_id = food.id

    response = client.get(
        f"/entries?month=2026-10&type=expense&category_id={category_id}"
    )

    assert response.status_code == 200
    assert "目标午餐".encode() in response.data
    assert "上月午餐".encode() not in response.data
    assert "目标工资".encode() not in response.data


def test_entries_default_to_current_month(app, client):
    with app.app_context():
        category = Category(name="餐饮", type="expense")
        db.session.add(category)
        db.session.commit()
        today = date.today()
        previous_month = today.replace(day=1) - __import__("datetime").timedelta(days=1)
        db.session.add_all(
            [
                Transaction(
                    type="expense",
                    category_id=category.id,
                    amount=Decimal("10.00"),
                    occurred_on=today,
                    note="本月默认记录",
                ),
                Transaction(
                    type="expense",
                    category_id=category.id,
                    amount=Decimal("20.00"),
                    occurred_on=previous_month,
                    note="上月排除记录",
                ),
            ]
        )
        db.session.commit()

    response = client.get("/entries")

    assert response.status_code == 200
    assert "本月默认记录".encode() in response.data
    assert "上月排除记录".encode() not in response.data


def test_entries_pagination_has_twenty_rows_per_page(app, client):
    with app.app_context():
        category = Category(name="餐饮", type="expense")
        db.session.add(category)
        db.session.commit()
        today = date.today()
        db.session.add_all(
            [
                Transaction(
                    type="expense",
                    category_id=category.id,
                    amount=Decimal("1.00"),
                    occurred_on=today,
                    note=f"分页记录 {index:02d}",
                )
                for index in range(21)
            ]
        )
        db.session.commit()

    first_page = client.get("/entries?month=" + date.today().strftime("%Y-%m"))
    second_page = client.get(
        "/entries?month=" + date.today().strftime("%Y-%m") + "&page=2"
    )

    assert first_page.status_code == 200
    assert "第 1 / 2 页".encode() in first_page.data
    assert first_page.data.count('data-label="日期"'.encode()) == 20
    assert second_page.data.count('data-label="日期"'.encode()) == 1
