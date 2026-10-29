def test_unknown_page_uses_custom_404(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert "页面没有找到".encode() in response.data
