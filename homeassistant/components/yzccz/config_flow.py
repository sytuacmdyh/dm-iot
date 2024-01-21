"""Config flow for remote_ctrl."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_flow

from .api import discover_devices
from .const import DOMAIN


async def _async_has_devices(hass: HomeAssistant) -> bool:
    """Return if there are devices that can be discovered."""
    # Check if there are any devices that can be discovered in the network.
    devices = await hass.async_add_executor_job(discover_devices)
    return len(devices) > 0


config_entry_flow.register_discovery_flow(DOMAIN, "remote_ctrl", _async_has_devices)
