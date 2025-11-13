from datetime import datetime, timezone

from lazy_tailscale.client.resources.device import Device


def device_is_online(device: Device) -> bool:
    if not device.last_seen:
        return False
    return (device.last_seen - datetime.now(timezone.utc)).total_seconds() < 500
