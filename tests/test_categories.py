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


def test_rejects_duplicate_category(app, client):
    first = client.post(
        "/categories",
        data={"name": "订阅", "type": "expense"},
        follow_redirects=True,
    )
    second = client.post(
        "/categories",
        data={"name": "订阅", "type": "expense"},
        follow_redirects=True,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert "同一类型下不能创建重名分类".encode() in second.data
    with app.app_context():
        assert Category.query.filter_by(name="订阅", type="expense").count() == 1
