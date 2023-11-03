from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator
from .walking_pad import WalkingPadApi


ENTITY_ID_FORMAT = DOMAIN + ".{}"


class WalkingPadEntity(CoordinatorEntity[WalkingPadCoordinator]):
    def __init__(self, name: str, walking_pad_api: WalkingPadApi, coordinator) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._walking_pad_api = walking_pad_api
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self._name, [])

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    async def async_update(self) -> None:
        await self._walking_pad_api.update_state()

    @property
    def device_info(self) -> dict[str, Any]:
        prop = {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._name,
            "manufacturer": "King Smith",
        }

        return prop

    @property
    def unique_id(self) -> str:
        """Return the unique id of the switch."""
        return self._walking_pad_api.mac

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        """Should poll."""
        return True

    @property
    def available(self):
        return self._walking_pad_api.connected
