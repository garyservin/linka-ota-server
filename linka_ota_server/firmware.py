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
from flask import current_app

# Release tracks a sensor can follow (see FirmwareVersion.get_for_track)
PRODUCTION = "production"
DEVEL = "devel"
TRACKS = (PRODUCTION, DEVEL)


class FirmwareVersion:
    def __init__(self, firmware, md5sum):
        # Expected format: <base_name>-v<version>.bin, where base_name may
        # itself contain "-v" (e.g. linka-v2-firmware-v1.0.0.bin)
        base_name, sep, version = firmware.removesuffix(".bin").rpartition("-v")
        if not sep or not base_name or not version:
            raise ValueError(
                f"Invalid firmware file name {firmware!r}, "
                "expected <name>-v<version>.bin"
            )
        self.base_name, self.version = base_name, version
        self.path = f"{current_app.config['FIRMWARE_PATH']}/{firmware}"
        self.md5sum = md5sum

    def __repr__(self):
        return f"{self.base_name}-v{self.version}.bin"

    @property
    def size(self):
        return os.path.getsize(self.path)

    @staticmethod
    def get_for_track(track=PRODUCTION):
        """Firmware a sensor following `track` should run.

        production: versions["latest"].
        devel:      versions["devel"], or production when that is newer or no devel
                    version is set, so devel sensors never fall behind production.
        """
        if track not in TRACKS:
            raise ValueError(f"Unknown track {track!r}, expected one of {TRACKS}")

        with open(current_app.config["FIRMWARE_PATH"] + "/" + "versions") as json_file:
            versions = json.load(json_file)

        version = versions["latest"]
        devel = versions.get("devel")
        if track == DEVEL and devel and version_key(devel) > version_key(version):
            version = devel
        return FirmwareVersion(versions[version]["file"], versions[version]["md5sum"])


def version_key(version):
    """Sort key for X.Y.Z[-prerelease] versions, following semver precedence.

    A pre-release sorts before its release (0.4.0-rc.1 < 0.4.0); pre-release
    identifiers compare numerically when they are numbers (rc.2 < rc.10).
    """
    release, _, prerelease = version.partition("-")
    numbers = tuple(int(part) for part in release.split("."))
    if not prerelease:
        return (numbers, 1, ())
    identifiers = tuple(
        (0, int(part), "") if part.isdigit() else (1, 0, part)
        for part in prerelease.split(".")
    )
    return (numbers, 0, identifiers)
