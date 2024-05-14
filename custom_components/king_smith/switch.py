"""Walking Pad Switch Entities."""
import logging

from datetime import timedelta

from homeassistant.components.switch import (
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    """Set up the entity."""
    treadmillName = config_entry.data.get(CONF_NAME) or DOMAIN
    data = hass.data[DOMAIN][config_entry.entry_id]

    entity = WalkingPadSwitch(treadmillName, data["device"], data["coordinator"])
    async_add_entities([entity])


class WalkingPadSwitch(WalkingPadEntity, SwitchEntity):
    """Representation of Walkingpad Switch."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        """Initialize the belt."""
        self._on = walking_pad_api.moving

        super().__init__(treadmillName, "", walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(
            "Updating walking pad belt switch entity: %s", self._walking_pad_api.moving
        )
        self._on = self._walking_pad_api.moving
        self.schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        """Handle the entity being added to hass."""
        await super().async_added_to_hass()
        try:
            await self._walking_pad_api.connect()
        except Exception as e:
            _LOGGER.warn("failed to connect to Walking Pad: %s", e)

    async def async_will_remove_from_hass(self) -> None:
        """Handle the entity being removed from hass."""
        await self._walking_pad_api.disconnect()
        return await super().async_will_remove_from_hass()

    @property
    def is_on(self):
        """Whether or not the switch is currrently on."""
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

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_switch"
