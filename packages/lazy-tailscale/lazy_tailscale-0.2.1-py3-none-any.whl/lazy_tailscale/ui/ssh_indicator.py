from textual.app import ComposeResult
from textual.widgets import Label


class SSHIndicator(Label):
    def __init__(self, ssh_enabled: bool | None):
        super().__init__()
        self.ssh_enabled = ssh_enabled

    def compose(self) -> ComposeResult:
        if self.ssh_enabled:
            yield Label("SSH ", classes="ssh-indicator")
        else:
            yield Label("    ", classes="ssh-indicator")
