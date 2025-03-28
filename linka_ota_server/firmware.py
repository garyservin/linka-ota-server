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
