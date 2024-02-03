"""Component to integrate ambilight for TVs exposing the Joint Space API."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MyUtil


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the configuration entry."""
    my_util = MyUtil(config_entry.data["host"])
    device_list = await my_util.get_device_list("电灯")
    async_add_entities(
        [SJMGLightEntity(device["name"], my_util) for device in device_list]
    )


class SJMGLightEntity(LightEntity):
    """自定义灯."""

    def __init__(self, device_name: str, util: MyUtil) -> None:
        """Initialize light."""
        self._attr_unique_id = device_name
        self._attr_assumed_state = True
        self._attr_should_poll = False

        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_is_on = False
        self._attr_icon = "mdi:lightbulb-outline"

        self.util = util

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self.util.do_action(self.unique_id, "turn-on")
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self.util.do_action(self.unique_id, "turn-off")
        self._attr_is_on = False
