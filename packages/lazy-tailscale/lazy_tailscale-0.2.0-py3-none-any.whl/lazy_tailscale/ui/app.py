from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.widgets import Footer

from lazy_tailscale.dependencies import AppDependencies
from lazy_tailscale.ui.device_detail import DeviceDetail
from lazy_tailscale.ui.device_list import DeviceListItem, DevicesList
from lazy_tailscale.ui.exit_node_detai import ExitNodeDetail
from lazy_tailscale.ui.exit_node_list import ExitNodeListItem, ExitNodesList
from lazy_tailscale.ui.notification import Notification
from lazy_tailscale.ui.status_badge import StatusBadge


class TailscaleTui(App):
    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("1", "focus_devices", "Focus Devices"),
        ("2", "focus_exit_nodes", "Focus Exit Nodes"),
    ]

    def __init__(self, deps: AppDependencies) -> None:
        super().__init__()
        self.dependencies = deps

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

    def compose(self) -> ComposeResult:
        self.notification_container = Container(id="notification-container")
        with Container(id="side-panel"):
            yield StatusBadge(self.dependencies)
            yield DevicesList(self.dependencies)
            yield ExitNodesList(self.dependencies)
        yield Container(id="detail-container")
        yield self.notification_container
        yield Footer()

    def action_cursor_down(self) -> None:
        self.screen.focus_next()

    def action_cursor_up(self) -> None:
        self.screen.focus_previous()

    def action_focus_devices(self) -> None:
        self.screen.query(DeviceListItem).first().focus()

    def action_focus_exit_nodes(self) -> None:
        try:
            self.screen.query(ExitNodeListItem).first().focus()
        except NoMatches:
            notification = Notification("No exit nodes available", variant="info")
            self.notification_container.mount(notification)

    @on(DeviceListItem.Focused)
    def focus_next_device(self, message: DeviceListItem.Focused) -> None:
        self.query_one("#detail-container").remove_children()
        self.query_one("#detail-container").mount(DeviceDetail(message.device))

    @on(DevicesList.SshConnectionError)
    def send_connection_error_notification(self, message: DevicesList.SshConnectionError) -> None:
        notification = Notification(f"   SSH into {message.device.name} failed.", variant="error")
        self.notification_container.mount(notification)

    @on(DevicesList.PingResult)
    def send_ping_result_notification(self, message: DevicesList.PingResult) -> None:
        if message.success:
            notification = Notification(f"   Ping received from {message.device.name} in {message.response_time} ms.")
        else:
            notification = Notification(f"   Ping to {message.device.name} failed.", variant="error")
        self.notification_container.mount(notification)

    @on(ExitNodeListItem.Focused)
    def focus_next_exit_node(self, message: ExitNodeListItem.Focused) -> None:
        try:
            detailed = self.query_one("#detail-container", Container)
            detailed.remove_children()
            detailed.mount(ExitNodeDetail(exit_node=message.exit_node))
        except NoMatches:
            # FIXME: This message should not be send when there are not exit nodes.
            pass
