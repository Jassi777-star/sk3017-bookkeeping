import calendar
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import extract, func

from app.extensions import db
from app.models import Category, Transaction
from app.services.periods import month_bounds, recent_months


def _number(value):
    return float(value or Decimal("0.00"))


def _apply_category_filter(query, category_id):
    if category_id is not None:
        return query.filter(Transaction.category_id == category_id)
    return query


def category_spending(month_start, category_id=None):
    start, end = month_bounds(month_start)
    query = (
        db.session.query(Category.id, Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.type == "expense",
            Transaction.occurred_on >= start,
            Transaction.occurred_on < end,
        )
    )
    query = _apply_category_filter(query, category_id)
    rows = (
        query.group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc(), Category.name)
        .all()
    )
    labels = [row[1] for row in rows]
    values = [_number(row[2]) for row in rows]
    return {
        "month": month_start.strftime("%Y-%m"),
        "total": round(sum(values), 2),
        "labels": labels,
        "values": values,
    }


def month_expense_total(month_start):
    start, end = month_bounds(month_start)
    total = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.type == "expense",
            Transaction.occurred_on >= start,
            Transaction.occurred_on < end,
        )
        .scalar()
    )
    return round(_number(total), 2)


def six_month_totals(end_month, category_id=None, count=6):
    months = recent_months(end_month, count)
    first_start, _ = month_bounds(months[0])
    _, final_end = month_bounds(months[-1])

    query = db.session.query(
        extract("year", Transaction.occurred_on),
        extract("month", Transaction.occurred_on),
        Transaction.type,
        func.sum(Transaction.amount),
    ).filter(
        Transaction.occurred_on >= first_start,
        Transaction.occurred_on < final_end,
    )
    query = _apply_category_filter(query, category_id)
    rows = query.group_by(
        extract("year", Transaction.occurred_on),
        extract("month", Transaction.occurred_on),
        Transaction.type,
    ).all()

    totals = defaultdict(lambda: {"income": Decimal("0.00"), "expense": Decimal("0.00")})
    for year, month, transaction_type, amount in rows:
        key = f"{int(year):04d}-{int(month):02d}"
        totals[key][transaction_type] = amount

    month_labels = [month.strftime("%Y-%m") for month in months]
    return {
        "months": month_labels,
        "income": [round(_number(totals[label]["income"]), 2) for label in month_labels],
        "expense": [round(_number(totals[label]["expense"]), 2) for label in month_labels],
    }


def daily_expenses(month_start, category_id=None):
    start, end = month_bounds(month_start)
    query = db.session.query(
        Transaction.occurred_on,
        func.sum(Transaction.amount),
    ).filter(
        Transaction.type == "expense",
        Transaction.occurred_on >= start,
        Transaction.occurred_on < end,
    )
    query = _apply_category_filter(query, category_id)
    rows = query.group_by(Transaction.occurred_on).all()
    totals = {occurred_on: amount for occurred_on, amount in rows}

    day_count = calendar.monthrange(month_start.year, month_start.month)[1]
    days = []
    values = []
    for day in range(1, day_count + 1):
        current = start.replace(day=day)
        days.append(current.isoformat())
        values.append(round(_number(totals.get(current)), 2))

    return {
        "month": month_start.strftime("%Y-%m"),
        "days": days,
        "expenses": values,
    }
