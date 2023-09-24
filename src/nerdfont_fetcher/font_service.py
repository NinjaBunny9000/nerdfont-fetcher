import os
import platform
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Callable

import requests
from rich.console import Console

console = Console(
    highlight=True,
)


class FontNotFoundError(Exception):
    def __init__(self, font_name):
        self.font_name = font_name
        self.message = f"Font {self.font_name} not found"


class FontManagementService:
    def __init__(
        self,
        font_name: str,
        on_skip: Optional[Callable[[str], None]] = None,
        on_install: Optional[Callable[[str], None]] = None,
        on_refresh_start: Optional[Callable[[], None]] = None,
        on_refresh_end: Optional[Callable[[], None]] = None,
        on_install_success: Optional[Callable[[], None]] = None,
    ):
        self.font_name = font_name
        self.on_skip = on_skip if on_skip else lambda *args: ...
        self.on_install = on_install if on_install else lambda *args: ...
        self.on_refresh_start = on_refresh_start if on_refresh_start else lambda: ...
        self.on_refresh_end = on_refresh_end if on_refresh_end else lambda: ...
        self.on_install_success = on_install_success if on_install_success else lambda: ...

        install_path_matrix = {
            "Linux": Path("~/.local/share/fonts").expanduser(),
            "Darwin": Path("~/Library/Fonts").expanduser(),
            "Windows": Path("C:/Windows/Fonts"),
        }

        self._install_path = install_path_matrix[platform.system()]

    @classmethod
    def get_font_zipfile_url(cls, font_name):
        # TODO move to data_source
        return f"https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/{font_name}.zip"

    def download_zip(self) -> tempfile.NamedTemporaryFile:
        url = self.get_font_zipfile_url(self.font_name)
        response = requests.get(url)
        response.raise_for_status()

        tmp_file = tempfile.NamedTemporaryFile(mode="wb+")
        tmp_file.write(response.content)
        tmp_file.seek(0)

        return tmp_file

    @staticmethod
    def make_needed_paths(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _extract_font_into_font_folder(self, zip_file, font_folder):
        files_installed = 0
        with zipfile.ZipFile(zip_file) as zipf:
            for file in zipf.namelist():
                if (font_folder / file).exists():
                    self.on_skip(file)
                elif file.endswith(".ttf") or file.endswith(".otf"):
                    self.on_install(file)
                    with zipf.open(file) as zf, open(str(Path(font_folder, file)), "wb+") as tfile:
                        shutil.copyfileobj(zf, tfile)
                        files_installed += 1
                    self.on_install_success()
        if files_installed:
            self.on_refresh_start()
            os.system("fc-cache -fv > /dev/null 2>&1")
            self.on_refresh_end()

    def install_fonts_from_zipfile(self, zip_file: tempfile.NamedTemporaryFile):
        final_font_path = Path(self._install_path, self.font_name)
        self.make_needed_paths(final_font_path)
        self._extract_font_into_font_folder(zip_file, final_font_path)
        return Path(final_font_path)
