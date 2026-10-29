from datetime import date

from flask import Blueprint, jsonify, render_template, request

from app.extensions import db
from app.models import Category, Transaction
from app.services.periods import parse_month
from app.services.statistics import (
    category_spending,
    daily_expenses,
    six_month_totals,
)


dashboard_bp = Blueprint("dashboard", __name__)


def _request_month(parameter="month"):
    value = request.args.get(parameter, "").strip()
    month = parse_month(value)
    if month is None:
        return None, jsonify({"error": "月份格式应为 YYYY-MM"})
    return month, None


def _request_category_id():
    value = request.args.get("category_id", "").strip()
    if not value:
        return None, None
    if not value.isdigit() or int(value) < 1:
        return None, jsonify({"error": "分类参数必须为正整数"})
    category_id = int(value)
    if db.session.get(Category, category_id) is None:
        return None, jsonify({"error": "分类不存在"})
    return category_id, None


@dashboard_bp.get("/dashboard")
def dashboard():
    month_value = request.args.get("month", date.today().strftime("%Y-%m"))
    category_value = request.args.get("category_id", "")
    return render_template(
        "dashboard.html",
        default_month=month_value,
        selected_category=category_value,
        categories=Category.query.order_by(Category.type, Category.name).all(),
        recent_transactions=Transaction.query.order_by(
            Transaction.occurred_on.desc(),
            Transaction.created_at.desc(),
        ).limit(6).all(),
    )


@dashboard_bp.get("/api/statistics/category")
def category_statistics():
    month, error = _request_month()
    if error:
        return error, 400
    category_id, error = _request_category_id()
    if error:
        return error, 400
    return jsonify(category_spending(month, category_id))


@dashboard_bp.get("/api/statistics/months")
def monthly_statistics():
    month, error = _request_month("end")
    if error:
        return error, 400
    category_id, error = _request_category_id()
    if error:
        return error, 400
    return jsonify(six_month_totals(month, category_id, count=6))


@dashboard_bp.get("/api/statistics/daily")
def daily_statistics():
    month, error = _request_month()
    if error:
        return error, 400
    category_id, error = _request_category_id()
    if error:
        return error, 400
    return jsonify(daily_expenses(month, category_id))
