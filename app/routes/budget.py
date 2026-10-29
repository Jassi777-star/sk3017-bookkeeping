import re
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.extensions import db
from app.models import MonthlyBudget
from app.services.periods import parse_month
from app.services.statistics import month_expense_total


budget_bp = Blueprint("budget", __name__)
AMOUNT_PATTERN = re.compile(r"^\d+(?:\.\d{1,2})?$")


def _budget_status(month):
    budget = MonthlyBudget.query.filter_by(month=month).first()
    expense = month_expense_total(month)
    total = _float(budget.total_amount) if budget else 0.0
    raw_ratio = expense / total if total else 0.0
    return {
        "month": month.strftime("%Y-%m"),
        "total_amount": total,
        "expense": expense,
        "remaining": round(max(total - expense, 0), 2),
        "usage_ratio": round(raw_ratio, 2),
        "has_budget": budget is not None,
        "alert": budget is not None and raw_ratio >= 0.8,
    }


def _float(value):
    return float(value or Decimal("0.00"))


@budget_bp.route("/budget", methods=["GET", "POST"])
def budget_page():
    month_value = request.values.get("month", date.today().strftime("%Y-%m"))
    month = parse_month(month_value)
    if month is None:
        flash("月份格式应为 YYYY-MM。", "error")
        month = date.today().replace(day=1)
        month_value = month.strftime("%Y-%m")

    if request.method == "POST":
        amount_value = request.form.get("total_amount", "").strip()
        if not AMOUNT_PATTERN.fullmatch(amount_value):
            flash("预算必须为非负数，且最多保留两位小数。", "error")
        else:
            try:
                amount = Decimal(amount_value)
            except InvalidOperation:
                flash("预算金额格式不正确。", "error")
            else:
                if amount > Decimal("9999999999.99"):
                    flash("预算金额超过允许范围。", "error")
                else:
                    record = MonthlyBudget.query.filter_by(month=month).first()
                    if record is None:
                        record = MonthlyBudget(month=month, total_amount=amount)
                        db.session.add(record)
                    else:
                        record.total_amount = amount
                    db.session.commit()
                    flash("月度预算已保存。", "success")
                    return redirect(url_for("budget.budget_page", month=month_value))

    status = _budget_status(month)
    return render_template("budget.html", month=month_value, status=status)


@budget_bp.get("/api/budget")
def budget_status():
    month_value = request.args.get("month", "").strip()
    month = parse_month(month_value)
    if month is None:
        return jsonify({"error": "月份格式应为 YYYY-MM"}), 400
    return jsonify(_budget_status(month))
