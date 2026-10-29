from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Category


categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_type = request.form.get("type", "").strip()

        if not name or len(name) > 50:
            flash("分类名称长度应为 1-50 个字符。", "error")
        elif category_type not in {"income", "expense"}:
            flash("请选择收入或支出类型。", "error")
        else:
            db.session.add(Category(name=name, type=category_type))
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("同一类型下不能创建重名分类。", "error")
            else:
                flash("分类创建成功。", "success")
                return redirect(url_for("categories.categories"))

    expense_categories = Category.query.filter_by(type="expense").order_by(Category.name).all()
    income_categories = Category.query.filter_by(type="income").order_by(Category.name).all()
    return render_template(
        "categories.html",
        expense_categories=expense_categories,
        income_categories=income_categories,
    )
