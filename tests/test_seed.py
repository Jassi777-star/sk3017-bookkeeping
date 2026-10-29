from app.cli import seed_demo_data
from app.models import Category, Transaction


def test_seed_demo_is_repeatable_and_creates_sixty_transactions(app):
    with app.app_context():
        assert seed_demo_data() is True
        assert Category.query.count() >= 11
        assert Transaction.query.count() >= 60
        assert Transaction.query.filter_by(type="income").count() > 0
        assert Transaction.query.filter_by(type="expense").count() > 0

        count_before = Transaction.query.count()
        assert seed_demo_data() is False
        assert Transaction.query.count() == count_before
