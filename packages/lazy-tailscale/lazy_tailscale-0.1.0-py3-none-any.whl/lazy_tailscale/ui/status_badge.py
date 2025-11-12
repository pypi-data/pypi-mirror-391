from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label, Static

from lazy_tailscale.dependencies import AppDependencies
from lazy_tailscale.local_client import NotConnectedError

REFREHSH_INTERVAL_SECONDS = 10


class StatusBadge(Static):
    status_text = reactive("")
    status_class = reactive("")

    def __init__(self, deps: AppDependencies):
        super().__init__()
        self.deps = deps
        self.border_title = "Tailnet"

    def compose(self) -> ComposeResult:
        yield Label(id="tailnet-label")
        yield Label(id="status-label")

    def on_mount(self) -> None:
        self.set_interval(REFREHSH_INTERVAL_SECONDS, self.update_status)
        self.update_status()

    def update_status(self) -> None:
        try:
            status = self.deps.local_service.get_status_info()
            is_online = status.self_info.online
            tailnet = status.current_tailnet.magic_dns_suffix

            tailnet_label = self.query_one("#tailnet-label", Label)
            status_label = self.query_one("#status-label", Label)

            tailnet_label.update(f"{tailnet} | ")

            if is_online:
                status_label.update("Online")
                status_label.set_class(True, "online")
                status_label.set_class(False, "offline")
            else:
                status_label.update("Offline")
                status_label.set_class(False, "online")
                status_label.set_class(True, "offline")

        except NotConnectedError:
            tailnet_label = self.query_one("#tailnet-label", Label)
            status_label = self.query_one("#status-label", Label)

            tailnet_label.update("Not Connected | ")
            status_label.update("Offline")
            status_label.set_class(False, "online")
            status_label.set_class(True, "offline")
