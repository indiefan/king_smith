
from datetime import timedelta

from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator
from .entity import WalkingPadEntity
from .walking_pad import WalkingPadApi


SCAN_INTERVAL = timedelta(seconds=5)
KPH_TO_MPH = 0.621371
MIN_VALUE = 0.0
MAX_VALUE = 4.0
STEP = 0.1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    name = config_entry.data.get(CONF_NAME) or DOMAIN
    data = hass.data[DOMAIN][config_entry.entry_id]

    entity = WalkingPadSpeed(name, data["device"], data["coordinator"])
    async_add_entities([entity])


class WalkingPadSpeed(WalkingPadEntity, NumberEntity):
    def __init__(
        self,
        name: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._name = f"{name} Speed"
        self._raw_kph = walking_pad_api.speed

        super().__init__(name, walking_pad_api, coordinator)

    def _raw_kph_to_mph(self, kph):
        if kph > 0:
            return round((kph * KPH_TO_MPH) / 10, 1)

        return kph

    def _mph_to_raw_kph(self, mph):
        if mph > 0:
            return round((mph * 10) / KPH_TO_MPH, 0)

        return mph

    @callback
    def _handle_coordinator_update(self) -> None:
        self._raw_kph = self._walking_pad_api.speed
        self.schedule_update_ha_state()

    @property
    def native_min_value(self) -> float:
        return MIN_VALUE

    @property
    def native_max_value(self) -> float:
        return MAX_VALUE

    @property
    def native_step(self) -> float | None:
        return STEP

    @property
    def native_value(self) -> float | None:
        return self._raw_kph_to_mph(self._raw_kph)

    async def async_set_native_value(self, value: float) -> None:
        kph_to_set = int(self._mph_to_raw_kph(value))

        self._raw_kph = kph_to_set
        await self._walking_pad_api.change_speed(kph_to_set)
        self.schedule_update_ha_state()
