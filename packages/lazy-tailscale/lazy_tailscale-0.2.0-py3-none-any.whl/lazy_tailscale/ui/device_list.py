from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, LoadingIndicator, Static

from lazy_tailscale.client.resources.device import Device
from lazy_tailscale.core import utils
from lazy_tailscale.dependencies import AppDependencies
from lazy_tailscale.ui.online_indicator import OnlineIndicator
from lazy_tailscale.ui.os_logo import OSLogo
from lazy_tailscale.ui.utils import clear_screen

from ..core.exceptions import PingTimeOutException, SSHConnectionException
from .ssh_indicator import SSHIndicator


class DeviceListItem(Static, can_focus=True):
    def __init__(self, device: Device):
        super().__init__()
        self.device = device
        self.change_count = 0

    def compose(self) -> ComposeResult:
        name = self.device.name.split(".")[0]
        yield OSLogo(self.device.os)
        yield Label(name, classes="device-name")
        yield LoadingIndicator()
        yield OnlineIndicator(utils.device_is_online(self.device))
        yield SSHIndicator(self.device.ssh_enabled)

    class Focused(Message):
        def __init__(self, device: Device) -> None:
            super().__init__()
            self.device = device

    def on_focus(self) -> None:
        self.post_message(self.Focused(self.device))

    def increment_change_count(self) -> None:
        self.change_count += 1
        self.query_one(LoadingIndicator).styles.visibility = "visible"

    def decrement_change_count(self) -> None:
        self.change_count -= 1
        if self.change_count <= 0:
            self.query_one(LoadingIndicator).styles.visibility = "hidden"


class DevicesList(VerticalScroll, can_focus=False):
    BINDINGS = [
        ("p", "ping_device()", "Ping device"),
        ("s", "ssh_device()", "SSH into device"),
    ]

    devices = reactive(list)

    def __init__(self, deps: AppDependencies):
        super().__init__()
        self.deps = deps

    def on_mount(self) -> None:
        self.border_title = "[1] Devices"
        self.set_timer(0.1, self.load_devices)

    def load_devices(self):
        self.devices = self.deps.remote_service.list_devices()

    def watch_devices(self, devices: list) -> None:
        self.remove_children()

        if devices:
            for device in devices:
                self.mount(DeviceListItem(device))

            self.query_one(DeviceListItem).focus()
        else:
            self.mount(Label("Loading devices..."))

    # TODO: Create different message for errors
    class PingResult(Message):
        def __init__(self, device: Device, success: bool, response_time: float | None, address: str | None) -> None:
            super().__init__()
            self.device = device
            self.success = success
            self.response_time = response_time
            self.address = address

    class SshConnectionError(Message):
        def __init__(self, device: Device) -> None:
            super().__init__()
            self.device = device

    @work(exclusive=True, thread=True)
    async def action_ping_device(self) -> None:
        device_list_item = self.query_one("DeviceListItem:focus", DeviceListItem)
        device_list_item.increment_change_count()
        device = device_list_item.device
        try:
            address, response_time = self.deps.remote_service.ping_device(device)
            self.post_message(self.PingResult(device, True, response_time, address))
        except ValueError:
            self.post_message(self.PingResult(device, False, None, None))
        except PingTimeOutException:
            self.post_message(self.PingResult(device, False, None, None))
        finally:
            device_list_item.decrement_change_count()

    def action_ssh_device(self) -> None:
        device = self.query_one("DeviceListItem:focus", DeviceListItem).device
        with self.app.suspend():
            try:
                clear_screen()
                print(f"Trying to SSH into: {device.hostname} ...")
                self.deps.remote_service.ssh_into_device(device)
            except SSHConnectionException:
                self.post_message(self.SshConnectionError(device))
