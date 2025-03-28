# Copyright 2022 Gary Servin
#
# This program is free software': 'you can redistribute it and/or modify
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

correct_headers = {
    'User-Agent': 'ESP8266-http-Update',
    'x-ESP8266-STA-MAC': '18:FE:AA:AA:AA:AA',
    'x-ESP8266-AP-MAC': '1A:FE:AA:AA:AA:AA',
    'x-ESP8266-free-space': '671744',
    'x-ESP8266-sketch-size': '373940',
    'x-ESP8266-sketch-md5': 'b185038c6e3a1786e0d2bc13d67d1061',
    'x-ESP8266-chip-size': '4194304',
    'x-ESP8266-sdk-version': '1.3.0',
    'x-ESP8266-version': '0.0.1',
}

def test_healthcheck(client):
    response = client.get('/up')
    assert response.status_code ==200

def test_wrong_route(client):
    response = client.get('/')
    assert response.status_code == 404

def test_wrong_headers(client):
    response = client.get('/ota')
    assert response.status_code == 403

def test_correct_headers(client):
    response = client.get('/ota', headers=correct_headers)
    assert response.status_code == 200

def test_correct_headers_no_update(client):
    headers = correct_headers.copy()
    headers['x-ESP8266-sketch-md5'] = 'c7f57af6623c7865ddbb6b564916aafd'
    headers['x-ESP8266-version'] = '0.0.2'
    response = client.get('/ota', headers=headers)
    assert response.status_code == 304

def test_latest_firmware(client):
    response = client.get("/latest_firmware")
    assert response.status_code == 200
    assert response.headers.get("Content-Length") == "6"
    assert response.headers.get("Content-Disposition") == "attachment; filename=linka-firmware-v0.0.2.bin"
    assert response.headers.get("Content-Type") == "application/octet-stream"

def test_latest_firmware_options(client):
    response = client.options("/latest_firmware")
    assert response.status_code == 200

def test_wrong_headers_not_allowed(client):
    headers = correct_headers.copy()
    headers['User-Agent'] = 'test'
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_STA_MAC_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-STA-MAC')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_AP_MAC_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-AP-MAC')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_free_space_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-free-space')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_sketch_size_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-sketch-size')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_sketch_md5_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-sketch-md5')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_chip_size_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-chip-size')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_sdk_version_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-sdk-version')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403

def test_wrong_headers_esp_version_missing(client):
    headers = correct_headers.copy()
    headers.pop('x-ESP8266-version')
    response = client.get('/ota', headers=headers)
    assert response.status_code == 403
