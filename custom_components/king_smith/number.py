"""Walking Pad Number Entities."""
from datetime import timedelta

from homeassistant.components.number import (
    NumberMode,
    NumberEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator
from .entity import WalkingPadEntity
from .walking_pad import WalkingPadApi


SCAN_INTERVAL = timedelta(seconds=5)
MIN_VALUE = 0.0
MAX_VALUE = 6.0
STEP = 0.1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entity."""
    treadmillName = config_entry.data.get(CONF_NAME) or DOMAIN
    data = hass.data[DOMAIN][config_entry.entry_id]

    entity = WalkingPadSpeed(treadmillName, data["device"], data["coordinator"])
    async_add_entities([entity])


class WalkingPadSpeed(WalkingPadEntity, NumberEntity):
    """Walking Pad Speed Entity."""

    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        """Initialize the Number entity."""
        self._kph = walking_pad_api.speed / 10.0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._kph = self._walking_pad_api.speed / 10
        self.schedule_update_ha_state()

    @property
    def native_min_value(self) -> float:
        """Minimum value."""
        return MIN_VALUE

    @property
    def native_max_value(self) -> float:
        """Maximum value."""
        return MAX_VALUE

    @property
    def native_step(self) -> float | None:
        """Step value."""
        return STEP

    @property
    def native_value(self) -> float | None:
        """Current value."""
        return self._kph

    async def async_set_native_value(self, value: float) -> None:
        """Set the speed."""
        await self._walking_pad_api.change_speed(int(value * 10))
        self.schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_speed"

    @property
    def name(self):
        """Name of the entity."""
        return "Speed"
