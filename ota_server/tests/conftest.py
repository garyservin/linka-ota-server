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
import pytest
import sys
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from app.service import create_app
from app.firmware import create_test_dir


@pytest.fixture
def client():
    app = create_app({'TESTING': True, 'FIRMWARE_PATH': '/tmp/bin'})

    with app.test_client() as client:
        with app.app_context():
            create_test_dir(app.config['FIRMWARE_PATH'])
        yield client

    shutil.rmtree(app.config['FIRMWARE_PATH'])
