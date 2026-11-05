from linka_ota_server import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_version_from_env(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    response = create_app({"TESTING": True}).test_client().get("/version")
    assert response.json == {"version": "1.2.3"}
