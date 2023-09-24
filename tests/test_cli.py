import zipfile
import re
from pathlib import Path
from unittest import mock
import platform
import pytest

from nerdfont_fetcher.font_service import FontManagementService


def test_font_install_mechanism():
    pytest.skip()


def test_incorrect_api_url():
    pytest.skip()


def test_incorrect_font_url():
    pytest.skip()


def test_parsing_github_release_info_for_fontlist(data_source):
    available_fonts = data_source.get_fonts()
    assert "3270" in available_fonts


def test_download_font(data_source, mock_font_file_contents):
    zip_tmp_file = data_source.download_font("TestFont")
    with zipfile.ZipFile(zip_tmp_file.name, "r") as zip_ref:
        with zip_ref.open("TestFont.ttf") as file:
            content = file.read()
            assert content == mock_font_file_contents


def test_install_linux(service_linux, data_source, mock_fs):
    zip_tmp_file = data_source.download_font("TestFont")
    font_path = service_linux.install_fonts_from_zipfile(zip_tmp_file)
    assert re.match(r"^/home/[^/]+/.local/share/fonts/TestFont$", str(font_path))


def test_install_macos(service_mac, data_source, mock_fs):
    zip_tmp_file = data_source.download_font("TestFont")
    with mock.patch.object(platform, "system", return_value="Darwin"):
        font_path = service_mac.install_fonts_from_zipfile(zip_tmp_file)
        print(font_path)
    assert re.match(r"^/Users/[^/]+/Library/Fonts/TestFont$", str(font_path))
