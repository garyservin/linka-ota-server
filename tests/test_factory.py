import os

from linka_ota_server import create_app

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_version_from_env(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    response = create_app({"TESTING": True}).test_client().get("/version")
    assert response.json == {"version": "1.2.3"}


def test_default_firmware_path(monkeypatch, tmp_path):
    # Must not depend on the directory the server is started from
    monkeypatch.delenv("FIRMWARE_PATH", raising=False)
    monkeypatch.chdir(tmp_path)
    assert create_app().config["FIRMWARE_PATH"] == os.path.join(ROOT_DIR, "bin")


def test_firmware_path_from_env(monkeypatch):
    monkeypatch.setenv("FIRMWARE_PATH", "/srv/firmware")
    assert create_app().config["FIRMWARE_PATH"] == "/srv/firmware"
