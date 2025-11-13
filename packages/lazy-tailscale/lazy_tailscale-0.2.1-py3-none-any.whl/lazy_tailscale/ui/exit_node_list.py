from logging import getLogger

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, Static

from lazy_tailscale.dependencies import AppDependencies
from lazy_tailscale.local_client import NotConnectedError

from ..local_client.status import PeerInfo

logger = getLogger(__name__)
REFREHSH_INTERVAL_SECONDS = 10


class ExitNodesList(VerticalScroll, can_focus=False):
    BINDINGS = [
        ("a", "activate_exit_node", "Activate Exit Node"),
        ("d", "deactivate_exit_node", "Deactivate Exit Node"),
    ]

    peers: reactive[dict[str, PeerInfo] | None] = reactive(None, init=False)

    def __init__(self, deps: AppDependencies):
        super().__init__()
        self.deps = deps
        self.border_title = "[2] Exit Nodes"

    def on_mount(self) -> None:
        self.load_peers()
        self.set_interval(REFREHSH_INTERVAL_SECONDS, self.load_peers)

    def compose(self) -> ComposeResult:
        yield Container(id="exit-nodes-container")

    def load_peers(self) -> None:
        try:
            status = self.deps.local_service.get_status_info()
            self.peers = status.peer
        except NotConnectedError:
            logger.info("Cannot load peers: Not connected to Tailscale")
            self.peers = {}

    def watch_peers(self, peers: dict[str, PeerInfo] | None) -> None:
        container = self.query_one("#exit-nodes-container", Container)

        if not peers:
            container.remove_children()
            return

        exit_nodes = {peer.host_name: peer for peer in peers.values() if peer.exit_node_option}
        existing_items = container.query(ExitNodeListItem)

        if not existing_items:
            container.mount_all([ExitNodeListItem(peer) for peer in exit_nodes.values()])
            return

        for item in existing_items:
            if peer := exit_nodes.pop(item.peer.host_name, None):
                item.peer = peer
            else:
                item.remove()

        for new_peer in exit_nodes.values():
            container.mount(ExitNodeListItem(new_peer))

    async def action_activate_exit_node(self) -> None:
        node = self.query_one("ExitNodeListItem:focus", ExitNodeListItem).peer
        self.deps.local_service.activate_exit_node(node.host_name)
        self.load_peers()

    async def action_deactivate_exit_node(self) -> None:
        self.deps.local_service.deactivate_exit_node()
        self.load_peers()


class ExitNodeListItem(Static, can_focus=True):
    peer: reactive[PeerInfo] = reactive(None)

    def __init__(self, peer: PeerInfo):
        super().__init__()
        self.peer = peer

    def compose(self) -> ComposeResult:
        yield Label(self.peer.host_name, id="hostname")
        if self.peer.exit_node:
            yield Label(" (Active)", classes="online", id="status")

    async def watch_peer(self, _new_peer: PeerInfo) -> None:
        if self.has_focus:
            self.post_message(self.Focused(self.peer))

        await self.recompose()

    class Focused(Message):
        def __init__(self, exit_node: PeerInfo) -> None:
            super().__init__()
            self.exit_node = exit_node

    def on_focus(self) -> None:
        self.post_message(self.Focused(self.peer))
