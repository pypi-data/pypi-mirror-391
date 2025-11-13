from textual.app import ComposeResult
from textual.widgets import Label


class OSLogo(Label):
    OS_LOGOS = {
        "linux": "",
        "windows": "\uf17a",
        "macos": "\uf179",
        "darwin": "\uf179",
        "ios": "\uf179",
        "android": "\uf17b",
        "freebsd": "\uf3a4",
        "openbsd": "\uf305",
    }
    DEFAULT_LOGO = "\uf128"  # Questionmark icon

    def __init__(self, os_name: str):
        super().__init__()
        self.os_name = os_name.lower()

    def compose(self) -> ComposeResult:
        logo = self.OS_LOGOS.get(self.os_name, self.DEFAULT_LOGO)
        yield Label(logo, classes="os-logo")
