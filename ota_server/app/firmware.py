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
import hashlib
import os
import re
from flask import current_app

class FirmwareVersion:
    def __init__(self, firmware, md5sum):
        self.base_name, self.version = re.split('-v', firmware)
        self.version = self.version.replace(".bin", "")
        self.path = f"{current_app.config['FIRMWARE_PATH']}/{firmware}"
        self.md5sum = md5sum

    def __repr__(self):
        return f"{self.base_name}-v{self.version}.bin"

    @property
    def md5(self):
        with open(path, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)

    @property
    def size(self):
        return os.path.getsize(self.path)

    @staticmethod
    def get_latest():
        """Get latest version from versions json file."""
        with open(current_app.config["FIRMWARE_PATH"] + '/' + 'versions') as json_file:
            versions = json.load(json_file)

        latest = versions["latest"]
        version = FirmwareVersion(versions[latest]["file"], versions[latest]["md5sum"])
        return version


def create_test_dir(path):
    versions = {
        "latest": "0.0.2",
        "0.0.1": {
            "file": "linka-firmware-v0.0.1.bin",
            "md5sum": "b185038c6e3a1786e0d2bc13d67d1061"
        },
        "0.0.2": {
            "file": "linka-firmware-v0.0.2.bin",
            "md5sum": "c7f57af6623c7865ddbb6b564916aafd"
        },
    }

    if not os.path.isdir(path):
        os.mkdir(path)
        with open(f"{path}/versions", 'w') as f:
            json.dump(versions, f)

        for version, data in versions.items():
            if "latest" in version:
                continue
            with open(f"{path}/{data['file']}", 'w') as f:
                f.write(f"v{version}")

    else:
        return
