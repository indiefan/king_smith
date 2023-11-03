from datetime import datetime
import logging
import time

from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ph4_walkingpad.pad import WalkingPadCurStatus

from .const import DOMAIN
from .walking_pad import WalkingPadApi

_LOGGER = logging.getLogger(__name__)

NEVER_TIME = -86400.0
DEBOUNCE_SECONDS = 1.0


class WalkingPadCoordinator(DataUpdateCoordinator[None]):
    """Data coordinator for receiving Walking Pad updates."""

    def __init__(self, hass: HomeAssistant, walking_pad_api: WalkingPadApi) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self._walking_pad_api = walking_pad_api
        self._walking_pad_api.register_status_callback(self._async_handle_update)
        self.connected = self._walking_pad_api.connected
        self._last_update_time = NEVER_TIME
        self._debounce_cancel: CALLBACK_TYPE | None = None
        self._debounced_update_job = HassJob(
            self._async_handle_debounced_update,
            f"Walking Pad {walking_pad_api.mac} BLE debounced update",
        )

    @callback
    def _async_handle_debounced_update(self, _now: datetime) -> None:
        """Handle debounced update."""
        self._debounce_cancel = None
        self._last_update_time = time.monotonic()
        self.async_set_updated_data(None)

    @callback
    def _async_handle_update(self, status: WalkingPadCurStatus) -> None:
        """Just trigger the callbacks."""
        self.connected = True
        previous_last_updated_time = self._last_update_time
        self._last_update_time = time.monotonic()
        if self._last_update_time - previous_last_updated_time >= DEBOUNCE_SECONDS:
            self.async_set_updated_data(None)
            return
        if self._debounce_cancel is None:
            self._debounce_cancel = async_call_later(
                self.hass, DEBOUNCE_SECONDS, self._debounced_update_job
            )

    @callback
    def _async_handle_disconnect(self) -> None:
        """Trigger the callbacks for disconnected."""
        self.connected = False
        self.async_update_listeners()

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._debounce_cancel is not None:
            self._debounce_cancel()
            self._debounce_cancel = None
        await super().async_shutdown()
