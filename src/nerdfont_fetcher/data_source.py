import tempfile

import requests
import requests_cache

requests_cache.install_cache(expire_after=3600)


class NerdFontsDataSource:
    BASE_URL = "https://api.github.com/repos/ryanoasis/nerd-fonts/releases"
    DOWNLOAD_BASE = "https://github.com/ryanoasis/nerd-fonts/releases/download"

    def __init__(self):
        self.available_fonts = []

    def _compile_latest_release_url(self):
        response = requests.get(f"{self.BASE_URL}/latest")
        release_data = response.json()
        latest_release_tag = release_data["tag_name"]
        return f"{self.BASE_URL}/tags/{latest_release_tag}"

    def _fetch_latest_release_tag(self):
        return requests.get(f"{self.BASE_URL}/latest").json()["tag_name"]

    def _fetch_font_zips_availabale(self):
        response = requests.get(f"{self.BASE_URL}/tags/{self._fetch_latest_release_tag()}")
        response.raise_for_status()
        data = response.json()
        return [asset["name"] for asset in data.get("assets", []) if asset["name"].endswith(".zip")]

    def download_font(self, font_name: str) -> tempfile.NamedTemporaryFile:
        response = requests.get(f"{self.DOWNLOAD_BASE}/{self._fetch_latest_release_tag()}/{font_name}.zip")
        response.raise_for_status()
        tmp_file = tempfile.NamedTemporaryFile(mode="wb+")
        tmp_file.write(response.content)
        tmp_file.seek(0)
        return tmp_file

    def get_fonts(self):
        font_zips = self._fetch_font_zips_availabale()
        return [font.replace(".zip", "") for font in font_zips]
