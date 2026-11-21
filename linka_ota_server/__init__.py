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

import os

from flask import (
    Flask,
    make_response,
    request,
    send_file,
    send_from_directory,
)

from .firmware import PRODUCTION, TRACKS, FirmwareVersion
from .headers import check_headers

# Matches /<route>/<track> for any known track, 404 otherwise
TRACK = f"<any({', '.join(TRACKS)}):track>"

# Directory containing the package: the repo root, or /app in the container
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (web flasher) live in <root>/static
STATIC_PATH = os.path.join(ROOT_PATH, "static")

# Firmware files and the versions file, unless FIRMWARE_PATH is set
DEFAULT_FIRMWARE_PATH = os.path.join(ROOT_PATH, "bin")


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Configure app
    app.config.from_mapping(
        FIRMWARE_PATH=os.environ.get("FIRMWARE_PATH", DEFAULT_FIRMWARE_PATH),
        # Set at image build time by CI (X.Y.Z for releases)
        APP_VERSION=os.environ.get("APP_VERSION", "dev"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/", methods=["GET"])
    def flasher():
        """Flasher page for linka sensors."""
        return send_from_directory(STATIC_PATH, "index.html")

    @app.route("/manifest.json", methods=["GET"])
    def manifest():
        """Serve the manifest.json file for the flasher."""
        return send_from_directory(STATIC_PATH, "manifest.json")

    @app.route("/up", methods=["GET"])
    def up():
        """Healtcheck for service."""
        return ""

    @app.route("/version", methods=["GET"])
    def version():
        """Version of the running service."""
        return {"version": app.config["APP_VERSION"]}

    # Serve /ota/production directly: sensors don't follow the redirect to /ota that
    # Flask would otherwise send for a URL matching a route's defaults
    app.url_map.redirect_defaults = False

    # Sensors follow production at /ota, or a track at /ota/<track> (e.g. /ota/devel)
    @app.route("/ota", methods=["GET"], defaults={"track": PRODUCTION})
    @app.route(f"/ota/{TRACK}", methods=["GET"])
    def ota(track):
        headers = request.headers

        # Check headers before we do anything
        result, message = check_headers(headers)
        if not result:
            return message, 403

        latest_firmware = FirmwareVersion.get_for_track(track)

        # If client already runs the track's version, skip
        if (
            latest_firmware.version == headers["x-ESP8266-version"]
            and headers["x-ESP8266-sketch-md5"] == latest_firmware.md5sum
        ):
            return "Not modified", 304

        response = make_response(
            send_file(
                latest_firmware.path,
                as_attachment=True,
                download_name=str(latest_firmware),
                mimetype="application/octet-stream",
            )
        )
        response.headers["x-MD5"] = latest_firmware.md5sum
        return response

    @app.route(
        "/latest_firmware", methods=["GET", "OPTIONS"], defaults={"track": PRODUCTION}
    )
    @app.route(f"/latest_firmware/{TRACK}", methods=["GET", "OPTIONS"])
    def latest_firmware(track):
        if request.method == "OPTIONS":  # CORS preflight
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "*")
            response.headers.add("Access-Control-Allow-Methods", "*")
            return response

        latest_firmware = FirmwareVersion.get_for_track(track)

        response = make_response(
            send_file(
                latest_firmware.path,
                as_attachment=True,
                download_name=str(latest_firmware),
                mimetype="application/octet-stream",
            )
        )
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    return app
