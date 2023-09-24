import json
import os
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock

from nerdfont_fetcher.data_source import NerdFontsDataSource
from nerdfont_fetcher.font_service import FontManagementService


@pytest.fixture
def mock_system_call():
    with patch("nerdfont_fetcher.cli.os.system", return_value=0) as mocked_function:
        yield mocked_function


@pytest.fixture
def service_mac(font_dir_macos):
    service = FontManagementService("TestFont")
    with patch.object(service, "_install_path", font_dir_macos):
        yield service


@pytest.fixture
def service_linux(font_dir_linux):
    service = FontManagementService("TestFont")
    with patch.object(service, "_install_path", font_dir_linux):
        yield service


@pytest.fixture
def font_dir_linux():
    return Path("/home/testuser/.local/share/fonts")


@pytest.fixture
def font_dir_macos():
    return Path("/Users/testuser/Library/Fonts")


@pytest.fixture
def tmp_download_dir():
    return Path(os.getcwd(), "output")


@pytest.fixture
def mock_os_operations():
    with patch("nerdfont_fetcher.font_service.os.path.exists", return_value=False) as exists_mock, patch(
        "nerdfont_fetcher.font_service.os.listdirs", return_value=["TestFont.ttf"]
    ) as listdir_mock:
        yield exists_mock, listdir_mock


@pytest.fixture
def mock_fs(mocker):
    mocker.patch("os.makedirs")
    mocker.patch("shutil.copy")
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.write", return_value=True)


@pytest.fixture
def mock_font_file_contents():
    return b"This is a test file inside the zip."


@pytest.fixture
def dummy_github_response_data():
    with open("tests/resources/mock_github_response.json") as f:
        return json.load(f)


@pytest.fixture
def zip_bytes(mock_font_file_contents):
    in_memory_zip = BytesIO()
    with zipfile.ZipFile(in_memory_zip, "w") as zf:
        zf.writestr("TestFont.ttf", mock_font_file_contents)
    in_memory_zip.seek(0)
    return in_memory_zip.read()


@pytest.fixture
def latest_release_url():
    return "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/tags/v3.0.6"


@pytest.fixture
def release_download_url():
    return "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.6"


@pytest.fixture
def mock_requests(release_download_url, latest_release_url, zip_bytes, dummy_github_response_data):
    mocked_url = f"{release_download_url}/TestFont.zip"
    with requests_mock.Mocker() as m:
        m.get(latest_release_url, json=dummy_github_response_data)
        m.get("https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest", json={"tag_name": "v3.0.6"})
        m.get(mocked_url, content=zip_bytes)
        yield m


@pytest.fixture()
def data_source(mock_requests):
    return NerdFontsDataSource()
