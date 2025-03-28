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

def check_headers(headers):
    # Check if the user agent is correct
    if headers.get("User-Agent", None) != "ESP8266-http-Update":
        return (False, "You are not allowed to reach this endpoint")

    # Check if headers are correct
    if not "x-ESP8266-STA-MAC" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-STA-MAC is missing",
        )
    elif not "x-ESP8266-AP-MAC" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-AP-MAC is missing",
        )
    elif not "x-ESP8266-free-space" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-free-space is missing",
        )
    elif not "x-ESP8266-sketch-size" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-sketch-size is missing",
        )
    elif not "x-ESP8266-sketch-md5" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-sketch-md5 is missing",
        )
    elif not "x-ESP8266-chip-size" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-chip-size is missing",
        )
    elif not "x-ESP8266-sdk-version" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-sdk-version is missing",
        )
    elif not "x-ESP8266-version" in headers:
        return (
            False,
            "You are not allowed to reach this endpoint, x-ESP8266-version is missing",
        )

    return (True, "")
