from textual.app import ComposeResult
from textual.widgets import Label


class OnlineIndicator(Label):
    def __init__(self, is_online: bool):
        super().__init__()
        self.is_online = is_online

    def compose(self) -> ComposeResult:
        if self.is_online:
            yield Label("Connected", classes="online")
        else:
            yield Label("󱐤  Offline", classes="offline")
