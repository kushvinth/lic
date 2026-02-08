"""Pytest configuration and shared fixtures for lic-cli tests."""

import pytest
from pathlib import Path
from datetime import datetime


@pytest.fixture
def mock_licenses_response():
    """Mock response for GitHub licenses API."""
    return [
        {
            "key": "mit",
            "name": "MIT License",
            "spdx_id": "MIT",
            "url": "https://api.github.com/licenses/mit",
            "node_id": "MDc6TGljZW5zZTEz"
        },
        {
            "key": "apache-2.0",
            "name": "Apache License 2.0",
            "spdx_id": "Apache-2.0",
            "url": "https://api.github.com/licenses/apache-2.0",
            "node_id": "MDc6TGljZW5zZTI="
        },
        {
            "key": "gpl-3.0",
            "name": "GNU General Public License v3.0",
            "spdx_id": "GPL-3.0",
            "url": "https://api.github.com/licenses/gpl-3.0",
            "node_id": "MDc6TGljZW5zZTk="
        }
    ]


@pytest.fixture
def mock_mit_license_body():
    """Mock MIT license body with placeholders."""
    return """MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


@pytest.fixture
def mock_apache_license_body():
    """Mock Apache 2.0 license body with placeholders."""
    return """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License."""


@pytest.fixture
def mock_license_response(mock_mit_license_body):
    """Mock response for specific license fetch."""
    return {
        "key": "mit",
        "name": "MIT License",
        "body": mock_mit_license_body,
        "description": "A short and simple permissive license with conditions only requiring preservation of copyright and license notices.",
        "implementation": "Create a text file (typically named LICENSE or LICENSE.txt) in the root of your source code and copy the text of the license into the file."
    }


@pytest.fixture
def temp_license_dir(tmp_path):
    """Create a temporary directory for license file tests."""
    return tmp_path


@pytest.fixture
def sample_author():
    """Sample author name for tests."""
    return "John Doe"


@pytest.fixture
def sample_year():
    """Sample year for tests."""
    return "2026"


@pytest.fixture
def current_year():
    """Get current year."""
    return str(datetime.now().year)
