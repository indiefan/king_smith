"""The Walking Pad Coordinator."""
from datetime import datetime, timezone
import logging
import time


from homeassistant.const import (
    ATTR_DEVICE_ID,
    ATTR_DOMAIN,
)

from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ph4_walkingpad.pad import WalkingPadCurStatus

from .const import DOMAIN, EVENT_SESSION_START, EVENT_SESSION_DONE
from .walking_pad import WalkingPadApi

_LOGGER = logging.getLogger(__name__)

NEVER_TIME = -86400.0
DEBOUNCE_SECONDS = 1.0


class WalkingPadCoordinator(DataUpdateCoordinator[None]):
    """Data coordinator for receiving Walking Pad updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        walking_pad_api: WalkingPadApi,
        device_id: str,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self._device_id = device_id
        self._last_status = None
        self._last_session = {}
        self._walking_pad_api = walking_pad_api
        self._walking_pad_api.register_status_callback(self._async_handle_update)
        self._walking_pad_api.register_status_callback(self._create_events)
        self.connected = self._walking_pad_api.connected
        self._last_update_time = NEVER_TIME
        self._debounce_cancel: CALLBACK_TYPE | None = None
        self._debounced_update_job = HassJob(
            self._async_handle_debounced_update,
            f"Walking Pad {walking_pad_api.mac} BLE debounced update",
        )

    @callback
    def _create_events(self, status: WalkingPadCurStatus) -> None:
        """Handle events for a Walking session."""
        if self._last_status is None:
            self._last_status = status
            return

        # Session has ended when time / duration is lower then before
        if self._last_status.time > 0 and self._last_status.time > status.time:
            # create last session info
            self._last_session = {
                "start_time": datetime.fromtimestamp(
                    time.time() - self._last_status.time, timezone.utc
                ),
                "end_time": datetime.fromtimestamp(time.time(), timezone.utc),
                "duration": self._last_status.time,
                "steps": self._last_status.steps,
                "dist": self._last_status.dist / 100,
                "avg_step_cadence": (self._last_status.steps / (float(self._last_status.time)/60)),
                "avg_speed": (
                    float(self._last_status.dist / 100)
                    / (float(self._last_status.time) / 3600.0)
                ),
            }

            # create event
            data = {
                "identifiers": {(DOMAIN, self._walking_pad_api.mac)},
                ATTR_DEVICE_ID: self._device_id,
                ATTR_DOMAIN: DOMAIN,
                **self._last_session,
            }
            self.hass.bus.fire(EVENT_SESSION_DONE, data)
        elif self._last_status.time == 0 and status.time > 0:
            # create event
            data = {
                "identifiers": {(DOMAIN, self._walking_pad_api.mac)},
                ATTR_DEVICE_ID: self._device_id,
                ATTR_DOMAIN: DOMAIN,
                "start_time": datetime.fromtimestamp(time.time(), timezone.utc),
            }
            self.hass.bus.fire(EVENT_SESSION_START, data)

        self._last_status = status

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
