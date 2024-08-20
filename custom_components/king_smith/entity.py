"""Shared Walking Pad Entity Base Class."""
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator
from .walking_pad import WalkingPadApi


ENTITY_ID_FORMAT = DOMAIN + ".{}"


class WalkingPadEntity(CoordinatorEntity[WalkingPadCoordinator]):
    """Walking Pad Entity Base Class."""

    def __init__(
        self, treadmillName: str, entityName: str, walking_pad_api: WalkingPadApi, coordinator
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._walking_pad_api = walking_pad_api
        self._treadmillName = treadmillName
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, f"{self._treadmillName} {entityName}", [])

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Handle an update."""
        await self._walking_pad_api.update_state()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return the device info."""
        prop = {
            "identifiers": {(DOMAIN, self._walking_pad_api.mac)},
            "name": self._treadmillName,
            "manufacturer": "King Smith",
        }

        return prop

    @property
    def should_poll(self):
        """Should poll."""
        return True

    @property
    def available(self) -> bool:
        """Return entity available state."""
        if self._walking_pad_api is not None and self._walking_pad_api.connected:
            return True
        return False
