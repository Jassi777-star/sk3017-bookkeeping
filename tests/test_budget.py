from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import Category, MonthlyBudget, Transaction


def test_can_create_and_update_monthly_budget(app, client):
    response = client.post(
        "/budget",
        data={"month": "2026-10", "total_amount": "2000.00"},
    )
    assert response.status_code == 302

    with app.app_context():
        budget = MonthlyBudget.query.one()
        assert budget.total_amount == Decimal("2000.00")

    response = client.post(
        "/budget",
        data={"month": "2026-10", "total_amount": "2500.00"},
    )
    assert response.status_code == 302

    with app.app_context():
        budget = MonthlyBudget.query.one()
        assert budget.total_amount == Decimal("2500.00")


def test_budget_api_reports_progress_and_alert(app, client):
    with app.app_context():
        category = Category(name="餐饮", type="expense")
        db.session.add(category)
        db.session.flush()
        db.session.add(
            MonthlyBudget(
                month=date(2026, 10, 1),
                total_amount=Decimal("1000.00"),
            )
        )
        db.session.add(
            Transaction(
                type="expense",
                category=category,
                amount=Decimal("850.00"),
                occurred_on=date(2026, 10, 10),
            )
        )
        db.session.commit()

    response = client.get("/api/budget?month=2026-10")

    assert response.status_code == 200
    assert response.get_json() == {
        "month": "2026-10",
        "total_amount": 1000.0,
        "expense": 850.0,
        "remaining": 150.0,
        "usage_ratio": 0.85,
        "has_budget": True,
        "alert": True,
    }


def test_budget_rejects_negative_amount(app, client):
    response = client.post(
        "/budget",
        data={"month": "2026-10", "total_amount": "-10.00"},
    )

    assert response.status_code == 200
    assert "预算必须为非负数".encode() in response.data
    with app.app_context():
        assert MonthlyBudget.query.count() == 0
