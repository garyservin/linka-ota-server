# Copyright 2022 Gary Servin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import json
import os
import pytest
import sys
import shutil

from linka_ota_server import create_app

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)


def create_test_dir(path):
    versions = {
        "latest": "0.0.2",
        "0.0.1": {
            "file": "linka-firmware-v0.0.1.bin",
            "md5sum": "b185038c6e3a1786e0d2bc13d67d1061",
        },
        "0.0.2": {
            "file": "linka-firmware-v0.0.2.bin",
            "md5sum": "c7f57af6623c7865ddbb6b564916aafd",
        },
    }

    if not os.path.isdir(path):
        os.mkdir(path)
        with open(f"{path}/versions", "w") as f:
            json.dump(versions, f)

        for version, data in versions.items():
            if "latest" in version:
                continue
            with open(f"{path}/{data['file']}", "w") as f:
                f.write(f"v{version}")

    else:
        return


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "FIRMWARE_PATH": "/tmp/bin"})

    with app.test_client() as client:
        with app.app_context():
            create_test_dir(app.config["FIRMWARE_PATH"])
        yield client

    shutil.rmtree(app.config["FIRMWARE_PATH"])
