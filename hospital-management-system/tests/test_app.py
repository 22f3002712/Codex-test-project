from backend.app import create_app


def test_health_page_renders():
    app = create_app()
    app.testing = True

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
