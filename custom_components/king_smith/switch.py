import asyncio
import logging

from datetime import timedelta
from typing import Any

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ph4_walkingpad import pad
from ph4_walkingpad.pad import WalkingPad, Controller, WalkingPadCurStatus

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator
from .entity import WalkingPadEntity
from .walking_pad import WalkingPadApi

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    name = config_entry.data.get(CONF_NAME) or DOMAIN
    data = hass.data[DOMAIN][config_entry.entry_id]

    entity = WalkingPadSwitch(name, data["device"], data["coordinator"])
    async_add_entities([entity])


class WalkingPadSwitch(WalkingPadEntity, SwitchEntity):
    """Representation of Walkingpad Switch."""

    def __init__(
        self,
        name: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        """Initialize the belt."""
        self._name = f"{name} Belt"
        self._on = walking_pad_api.moving

        super().__init__(name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(
            "Updating walking pad belt switch entity: %s", self._walking_pad_api.moving
        )
        self._on = self._walking_pad_api.moving
        self.schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        await self._walking_pad_api.connect()

    async def async_will_remove_from_hass(self) -> None:
        await self._walking_pad_api.disconnect()
        return await super().async_will_remove_from_hass()

    @property
    def is_on(self):
        return self._on

    async def async_turn_on(self):
        """Turn On."""
        self._on = True
        await self._walking_pad_api.turn_on()
        await self._walking_pad_api.start_belt()
        self.schedule_update_ha_state()

    async def async_turn_off(self):
        """Turn Off."""
        if self._walking_pad_api.moving:
            await self._walking_pad_api.stop_belt()

        await self._walking_pad_api.turn_off()
        self._on = False
        self.schedule_update_ha_state()
