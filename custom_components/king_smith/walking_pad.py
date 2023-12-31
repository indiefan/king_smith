"""Walking Pad Api."""
import asyncio
import logging
import time

from bleak.backends.device import BLEDevice

from ph4_walkingpad.pad import Controller, WalkingPad, WalkingPadCurStatus

STATUS_LOCK_ON_CMD_SECONDS = 5

_LOGGER = logging.getLogger(__name__)


class WalkingPadApi:
    """Walkingpad device."""

    def __init__(self, name: str, ble_device: BLEDevice) -> None:
        """Create a new walking pad api instance."""
        self._name = name
        self._ble_device = ble_device
        self._ctrl = Controller()
        self._callbacks = []
        self._status_lock = False
        self._last_cmd_time = time.time()

        self._connected = False
        self._moving = False
        self._speed = 0
        self._distance = 0

        self._register_controller_callbacks()

    def _register_controller_callbacks(self):
        self._ctrl.handler_cur_status = self._on_status_update

    def _begin_cmd(self) -> asyncio.Lock:
        self._status_lock = True
        return asyncio.Lock()

    async def _end_cmd(self):
        await asyncio.sleep(0.75)
        self._last_cmd_time = time.time()
        self._status_lock = False

    def _on_status_update(self, sender, status: WalkingPadCurStatus) -> None:
        """Update current state."""
        # Don't update if we're still running a command or just did (status from device is outdated at first)
        if (
            self._status_lock
            or time.time() - self._last_cmd_time < STATUS_LOCK_ON_CMD_SECONDS
        ):
            return

        self._moving = status.speed > 0
        self._speed = status.speed
        self._distance = status.dist

        if len(self._callbacks) > 0:
            for callback in self._callbacks:
                callback(status)

    def register_status_callback(self, callback) -> None:
        """Register a status callback."""
        self._callbacks.append(callback)

    @property
    def mac(self):
        """Mac address."""
        return self._ble_device.address

    @property
    def name(self):
        """Name."""
        return self._name

    @property
    def connected(self):
        """Connected status."""
        return self._connected

    @property
    def moving(self):
        """Whether or not the device is currently moving."""
        return self._moving

    @property
    def speed(self):
        """The current device speed."""
        return self._speed

    @property
    def distance(self):
        """The current device distance."""
        return self._distance

    async def connect(self) -> None:
        """Connect the device."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.run(self._ble_device)
            self._connected = True
            await self._end_cmd()

    async def disconnect(self) -> None:
        """Disconnect the device."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.disconnect()
            self._connected = False
            await self._end_cmd()

    async def turn_on(self) -> None:
        """Turn on the device."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.switch_mode(WalkingPad.MODE_MANUAL)
            await self._end_cmd()

    async def turn_off(self) -> None:
        """Turn off the device."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.switch_mode(WalkingPad.MODE_STANDBY)
            await self._end_cmd()

    async def start_belt(self) -> None:
        """Start the belt."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.start_belt()
            self._moving = True
            await self._end_cmd()

    async def stop_belt(self) -> None:
        """Stop the belt."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.stop_belt()
            self._moving = False
            await self._end_cmd()

    async def change_speed(self, speed: int) -> None:
        """Change the speed."""
        lock = self._begin_cmd()
        async with lock:
            await self._ctrl.change_speed(speed)
            self._speed = speed
            await self._end_cmd()

    async def update_state(self) -> None:
        """Update device state."""
        # Grab the lock so we don't run while another command is running
        lock = self._begin_cmd()
        async with lock:
            # Disable status lock so our update triggers a refresh
            self._status_lock = False
            await self._ctrl.ask_stats()
            # Skip callback so we don't reset debouncer
