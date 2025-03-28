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
)

from .firmware import FirmwareVersion
from .headers import check_headers

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Configure app
    app.config.from_mapping(
        FIRMWARE_PATH=os.environ.get("FIRMWARE_PATH", "../bin")
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/up", methods=["GET"])
    def up():
        """Healtcheck for service."""
        return ""

    @app.route("/ota", methods=['GET'])
    def ota():
        headers = request.headers

        # Check headers before we do anything
        result, message = check_headers(headers)
        if not result:
            return message, 403

        # Get latest version
        latest_firmware = FirmwareVersion.get_latest()

        # If client has the same version as the latest one, skip
        if latest_firmware.version == headers["x-ESP8266-version"]:
            return "Not modified", 304

        if (
            latest_firmware.version != headers["x-ESP8266-version"]
            or headers["x-ESP8266-sketch-md5"] != latest_firmware.md5sum
        ):

            response = make_response(
                send_file(
                    latest_firmware.path,
                    as_attachment=True,
                    download_name=str(latest_firmware),
                    mimetype="application/octet-stream",
                )
            )
            response.headers["Content-Length"] = latest_firmware.size
            response.headers["x-MD5"] = latest_firmware.md5sum
            return response

        return "Not modified", 304

    @app.route("/latest_firmware", methods=['GET', 'OPTIONS'])
    def latest_firmware():
        if request.method == "OPTIONS": # CORS preflight
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response

        # Get latest version
        latest_firmware = FirmwareVersion.get_latest()

        response = make_response(
            send_file(
                latest_firmware.path,
                as_attachment=True,
                download_name=str(latest_firmware),
                mimetype="application/octet-stream",
            )
        )
        response.headers.add("Content-Length", latest_firmware.size)
        response.headers.add("Access-Control-Allow-Origin","*")
        return response

    return app


