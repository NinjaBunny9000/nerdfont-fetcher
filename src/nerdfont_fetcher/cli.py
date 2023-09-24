from InquirerPy import inquirer
from InquirerPy.validator import ValidationError
from prompt_toolkit.completion import WordCompleter
from rich import print
from rich.columns import Columns
from rich.console import Console

from .data_source import NerdFontsDataSource
from .font_service import FontManagementService

console = Console()


def display_font_options_in_columns(fonts):
    console.rule("Available fonts:", style="red bold")
    console.print()
    print(Columns(fonts, equal=True))
    console.print()
    console.rule("Make a Selection:", style="blue bold")


def on_skip(file):
    console.print(f"Skipping {file}.. (already installed)")


def on_install(file):
    console.print(f"Installing {file}...", end=" ")


def on_install_success():
    console.print(":thumbs_up:")


def on_refresh_start():
    console.print(":hourglass: Refreshing font cache...", end=" ")


def on_refresh_end():
    console.print("Done!")


def ui():
    source = NerdFontsDataSource()
    available_fonts = source.get_fonts()

    display_font_options_in_columns(available_fonts)

    def font_validator(response: str):
        if response.lower() not in [font.lower() for font in available_fonts]:
            raise ValidationError(message="Font not found!", cursor_position=len(response))
        else:
            return True

    font_completer = WordCompleter(available_fonts, ignore_case=True)
    print()

    install_another = True
    while install_another:
        console.print()
        font_name = inquirer.text(
            message="Which font do you want to install?:",
            completer=font_completer,
            multicolumn_complete=True,
            validate=font_validator,
        ).execute()

        console.print(f"Installing {font_name}...")

        tmp_file = source.download_font(font_name)

        service = FontManagementService(
            font_name,
            on_skip=on_skip,
            on_install=on_install,
            on_refresh_start=on_refresh_start,
            on_refresh_end=on_refresh_end,
            on_install_success=on_install_success,
        )
        install_path = service.install_fonts_from_zipfile(tmp_file)
        console.print(f"\n:tada: {font_name} installed successfully at {install_path}\n")

        install_another = inquirer.confirm(
            message="Would you like to install another font?",
            default=False,
        ).execute()
        console.print()
    exit()


def main():
    try:
        ui()
    except KeyboardInterrupt:
        exit()
