from textual.app import ComposeResult
from textual.widgets import Pretty, Static

from lazy_tailscale.local_client.status import PeerInfo


class ExitNodeDetail(Static):
    def __init__(self, exit_node: PeerInfo):
        super().__init__()

        self.border_title = exit_node.host_name
        self.exit_node = exit_node

    def compose(self) -> ComposeResult:
        yield Pretty(self.exit_node)
