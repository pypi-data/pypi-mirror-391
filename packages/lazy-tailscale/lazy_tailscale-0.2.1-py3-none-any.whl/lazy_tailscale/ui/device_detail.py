from textual.app import ComposeResult
from textual.widgets import Pretty, Static

from lazy_tailscale.client.resources.device import Device


class DeviceDetail(Static):
    def __init__(self, device: Device):
        super().__init__()

        self.border_title = device.name
        self.device = device

    def compose(self) -> ComposeResult:
        yield Pretty(self.device)
