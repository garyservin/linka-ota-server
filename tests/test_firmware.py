import pytest

from linka_ota_server import create_app
from linka_ota_server.firmware import FirmwareVersion


@pytest.fixture
def app_context():
    app = create_app({"TESTING": True, "FIRMWARE_PATH": "/firmware"})
    with app.app_context():
        yield


@pytest.mark.parametrize(
    "filename, base_name, version",
    [
        ("linka-firmware-v0.0.1.bin", "linka-firmware", "0.0.1"),
        ("linka-firmware-v0.3.2.bin", "linka-firmware", "0.3.2"),
        # Base names containing "-v" used to raise ValueError
        ("linka-v2-firmware-v1.0.0.bin", "linka-v2-firmware", "1.0.0"),
        ("linka-firmware-vpro-v0.1.0.bin", "linka-firmware-vpro", "0.1.0"),
    ],
)
def test_parse_filename(app_context, filename, base_name, version):
    firmware = FirmwareVersion(filename, "md5")
    assert firmware.base_name == base_name
    assert firmware.version == version
    assert firmware.path == f"/firmware/{filename}"
    assert str(firmware) == filename


@pytest.mark.parametrize("filename", ["linka-firmware.bin", "firmware-0.1.0.bin"])
def test_parse_filename_without_version(app_context, filename):
    with pytest.raises(ValueError, match="-v<version>.bin"):
        FirmwareVersion(filename, "md5")
