import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models import Category, Transaction
from app.services.periods import month_bounds, parse_month


entries_bp = Blueprint("entries", __name__, url_prefix="/entries")

AMOUNT_PATTERN = re.compile(r"^\d+(?:\.\d{1,2})?$")


def _parse_entry_form():
    form = {
        "type": request.form.get("type", "").strip(),
        "category_id": request.form.get("category_id", "").strip(),
        "amount": request.form.get("amount", "").strip(),
        "occurred_on": request.form.get("occurred_on", "").strip(),
        "note": request.form.get("note", "").strip(),
    }
    errors = {}
    category = None
    amount = None
    occurred_on = None

    if form["type"] not in {"income", "expense"}:
        errors["type"] = "请选择收入或支出类型。"

    try:
        category_id = int(form["category_id"])
    except ValueError:
        errors["category_id"] = "请选择分类。"
    else:
        category = db.session.get(Category, category_id)
        if category is None:
            errors["category_id"] = "所选分类不存在。"
        elif form["type"] and category.type != form["type"]:
            errors["category_id"] = "分类与收支类型不一致。"

    if not AMOUNT_PATTERN.fullmatch(form["amount"]):
        errors["amount"] = "金额必须为非负数，且最多保留两位小数。"
    else:
        try:
            amount = Decimal(form["amount"])
        except InvalidOperation:
            errors["amount"] = "金额格式不正确。"
        else:
            if amount > Decimal("9999999999.99"):
                errors["amount"] = "金额超过允许范围。"

    if len(form["note"]) > 255:
        errors["note"] = "备注不能超过 255 个字符。"

    try:
        occurred_on = datetime.strptime(form["occurred_on"], "%Y-%m-%d").date()
    except ValueError:
        errors["occurred_on"] = "日期格式应为 YYYY-MM-DD。"

    return form, errors, category, amount, occurred_on


@entries_bp.route("")
def entries():
    if "month" in request.args:
        month_value = request.args.get("month", "").strip()
    else:
        month_value = date.today().strftime("%Y-%m")
    selected_type = request.args.get("type", "").strip()
    category_value = request.args.get("category_id", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Transaction.query
    month = parse_month(month_value)
    if month:
        start, end = month_bounds(month)
        query = query.filter(
            Transaction.occurred_on >= start,
            Transaction.occurred_on < end,
        )
    if selected_type in {"income", "expense"}:
        query = query.filter(Transaction.type == selected_type)
    if category_value.isdigit() and int(category_value) > 0:
        query = query.filter(Transaction.category_id == int(category_value))

    pagination = query.order_by(
        Transaction.occurred_on.desc(),
        Transaction.created_at.desc(),
    ).paginate(page=max(page, 1), per_page=20, error_out=False)
    return render_template(
        "entries/list.html",
        transactions=pagination.items,
        pagination=pagination,
        categories=Category.query.order_by(Category.type, Category.name).all(),
        filters={
            "month": month_value,
            "type": selected_type,
            "category_id": category_value,
        },
    )


@entries_bp.route("/new", methods=["GET", "POST"])
def new_entry():
    form = {
        "type": "expense",
        "category_id": "",
        "amount": "",
        "occurred_on": date.today().isoformat(),
        "note": "",
    }
    errors = {}

    if request.method == "POST":
        form, errors, category, amount, occurred_on = _parse_entry_form()
        if not errors:
            transaction = Transaction(
                type=form["type"],
                category=category,
                amount=amount,
                occurred_on=occurred_on,
                note=form["note"] or None,
            )
            db.session.add(transaction)
            db.session.commit()
            flash("交易保存成功。", "success")
            return redirect(url_for("entries.entries"))

    return render_template(
        "entries/form.html",
        form=form,
        errors=errors,
        categories=Category.query.order_by(Category.type, Category.name).all(),
        heading="新增交易",
        action=url_for("entries.new_entry"),
    )


@entries_bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
def edit_entry(entry_id):
    transaction = db.get_or_404(Transaction, entry_id)
    form = {
        "type": transaction.type,
        "category_id": str(transaction.category_id),
        "amount": f"{transaction.amount:.2f}",
        "occurred_on": transaction.occurred_on.isoformat(),
        "note": transaction.note or "",
    }
    errors = {}

    if request.method == "POST":
        form, errors, category, amount, occurred_on = _parse_entry_form()
        if not errors:
            transaction.type = form["type"]
            transaction.category = category
            transaction.amount = amount
            transaction.occurred_on = occurred_on
            transaction.note = form["note"] or None
            db.session.commit()
            flash("交易修改成功。", "success")
            return redirect(url_for("entries.entries"))

    return render_template(
        "entries/form.html",
        form=form,
        errors=errors,
        categories=Category.query.order_by(Category.type, Category.name).all(),
        heading="编辑交易",
        action=url_for("entries.edit_entry", entry_id=entry_id),
    )


@entries_bp.route("/<int:entry_id>/delete", methods=["POST"])
def delete_entry(entry_id):
    transaction = db.get_or_404(Transaction, entry_id)
    db.session.delete(transaction)
    db.session.commit()
    flash("交易已删除。", "success")
    return redirect(url_for("entries.entries"))
