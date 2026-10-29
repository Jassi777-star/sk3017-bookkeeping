from app.models import Category


def test_can_create_expense_category(app, client):
    response = client.post(
        "/categories",
        data={"name": "早餐", "type": "expense"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"\xe6\x97\xa9\xe9\xa4\x90" in response.data

    with app.app_context():
        category = Category.query.filter_by(name="早餐", type="expense").first()
        assert category is not None
