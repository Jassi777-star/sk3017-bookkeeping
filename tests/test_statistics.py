from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Category, Transaction


@pytest.fixture()
def statistics_data(app):
    with app.app_context():
        food = Category(name="餐饮", type="expense")
        transport = Category(name="交通", type="expense")
        salary = Category(name="工资", type="income")
        db.session.add_all([food, transport, salary])
        db.session.commit()
        db.session.add_all(
            [
                Transaction(
                    type="expense",
                    category_id=food.id,
                    amount=Decimal("100.00"),
                    occurred_on=date(2026, 10, 2),
                ),
                Transaction(
                    type="expense",
                    category_id=food.id,
                    amount=Decimal("50.00"),
                    occurred_on=date(2026, 10, 2),
                ),
                Transaction(
                    type="expense",
                    category_id=transport.id,
                    amount=Decimal("20.00"),
                    occurred_on=date(2026, 10, 3),
                ),
                Transaction(
                    type="income",
                    category_id=salary.id,
                    amount=Decimal("5000.00"),
                    occurred_on=date(2026, 5, 1),
                ),
                Transaction(
                    type="income",
                    category_id=salary.id,
                    amount=Decimal("5200.00"),
                    occurred_on=date(2026, 10, 1),
                ),
            ]
        )
        db.session.commit()
        return {
            "food_id": food.id,
            "transport_id": transport.id,
        }


def test_category_statistics_aggregate_expenses(client, statistics_data):
    response = client.get("/api/statistics/category?month=2026-10")

    assert response.status_code == 200
    assert response.get_json() == {
        "month": "2026-10",
        "total": 170.0,
        "labels": ["餐饮", "交通"],
        "values": [150.0, 20.0],
    }


def test_category_statistics_can_filter_by_category(client, statistics_data):
    response = client.get(
        f"/api/statistics/category?month=2026-10&category_id={statistics_data['food_id']}"
    )

    assert response.status_code == 200
    assert response.get_json()["labels"] == ["餐饮"]
    assert response.get_json()["total"] == 150.0


def test_monthly_statistics_fill_missing_months(client, statistics_data):
    response = client.get("/api/statistics/months?end=2026-10&count=6")

    assert response.status_code == 200
    data = response.get_json()
    assert data["months"] == [
        "2026-05",
        "2026-06",
        "2026-07",
        "2026-08",
        "2026-09",
        "2026-10",
    ]
    assert data["income"] == [5000.0, 0.0, 0.0, 0.0, 0.0, 5200.0]
    assert data["expense"] == [0.0, 0.0, 0.0, 0.0, 0.0, 170.0]


def test_daily_statistics_fill_days_without_expense(client, statistics_data):
    response = client.get("/api/statistics/daily?month=2026-10")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["days"]) == 31
    assert data["expenses"][0] == 0.0
    assert data["expenses"][1] == 150.0
    assert data["expenses"][2] == 20.0
    assert data["expenses"][-1] == 0.0


def test_statistics_reject_invalid_month(client):
    response = client.get("/api/statistics/category?month=2026-13")

    assert response.status_code == 400
    assert "月份格式应为 YYYY-MM" in response.get_json()["error"]
