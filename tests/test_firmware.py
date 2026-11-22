import json

import pytest

from linka_ota_server import create_app
from linka_ota_server.firmware import DEVEL, PRODUCTION, FirmwareVersion, version_key


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


@pytest.mark.parametrize(
    "older, newer",
    [
        ("0.3.2", "0.4.0"),
        ("0.9.0", "0.10.0"),
        ("0.4.0-rc.1", "0.4.0"),
        ("0.3.2", "0.4.0-rc.1"),
        ("0.4.0-rc.2", "0.4.0-rc.10"),
        ("0.4.0-alpha", "0.4.0-beta"),
        ("0.4.0-rc.1", "0.4.0-rc.1.1"),
    ],
)
def test_version_order(older, newer):
    assert version_key(older) < version_key(newer)


def write_versions(path, latest, devel=None, extra=()):
    versions = {"latest": latest}
    if devel:
        versions["devel"] = devel
    for version in {latest, devel, *extra} - {None}:
        versions[version] = {
            "file": f"linka-firmware-v{version}.bin",
            "md5sum": version,
        }
    (path / "versions").write_text(json.dumps(versions))


@pytest.fixture
def firmware_dir(tmp_path):
    app = create_app({"TESTING": True, "FIRMWARE_PATH": str(tmp_path)})
    with app.app_context():
        yield tmp_path


@pytest.mark.parametrize(
    "latest, devel, production_version, devel_version",
    [
        # No devel version: devel sensors follow production
        ("0.3.2", None, "0.3.2", "0.3.2"),
        # Pre-release on devel only
        ("0.3.2", "0.4.0-rc.1", "0.3.2", "0.4.0-rc.1"),
        # Released after the release candidate: devel moves on to the release
        ("0.4.0", "0.4.0-rc.1", "0.4.0", "0.4.0"),
        # Same version on both
        ("0.4.0", "0.4.0", "0.4.0", "0.4.0"),
    ],
)
def test_get_for_track(firmware_dir, latest, devel, production_version, devel_version):
    write_versions(firmware_dir, latest, devel)
    assert FirmwareVersion.get_for_track().version == production_version
    assert FirmwareVersion.get_for_track(PRODUCTION).version == production_version
    assert FirmwareVersion.get_for_track(DEVEL).version == devel_version


def test_get_for_unknown_track(firmware_dir):
    write_versions(firmware_dir, "0.3.2")
    with pytest.raises(ValueError, match="Unknown track"):
        FirmwareVersion.get_for_track("beta")
