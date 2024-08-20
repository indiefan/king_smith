"""Platform sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    RestoreSensor,
)
from homeassistant.components.sensor.const import UnitOfTime
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import CONF_NAME, UnitOfLength, UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from custom_components.king_smith.const import DOMAIN
from custom_components.king_smith.coordinator import WalkingPadCoordinator
from custom_components.king_smith.entity import WalkingPadEntity

from custom_components.king_smith.walking_pad import WalkingPadApi


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entity."""
    treadmillName = config_entry.data.get(CONF_NAME) or DOMAIN
    data = hass.data[DOMAIN][config_entry.entry_id]
    walking_pad_api = data["device"]
    coordinator = data["coordinator"]

    distanceEntity = DistanceSensor(treadmillName, walking_pad_api, coordinator)
    timeEntity = TimeSensor(treadmillName, walking_pad_api, coordinator)
    speedEntity = SpeedSensor(treadmillName, walking_pad_api, coordinator)
    stepsEntity = StepsSensor(treadmillName, walking_pad_api, coordinator)
    stepCadenceEntity = StepCadenceSensor(treadmillName, walking_pad_api, coordinator)

    totalDistanceEntity = TotalDistanceSensor(
        treadmillName, walking_pad_api, coordinator
    )
    totalTimeEntity = TotalTimeSensor(treadmillName, walking_pad_api, coordinator)
    totalStepsEntity = TotalStepsSensor(treadmillName, walking_pad_api, coordinator)

    async_add_entities(
        [
            distanceEntity,
            timeEntity,
            speedEntity,
            stepsEntity,
            totalDistanceEntity,
            totalTimeEntity,
            totalStepsEntity,
            stepCadenceEntity,
        ]
    )


class DistanceSensor(WalkingPadEntity, SensorEntity):
    """Session Distance walked in the current session."""

    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0.0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._state = self._walking_pad_api.distance / 100
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_distance"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Distance"


class TimeSensor(WalkingPadEntity, SensorEntity):
    """Session Time walked in the current session."""

    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._state = self._walking_pad_api.time
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_time"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Duration"


class SpeedSensor(WalkingPadEntity, SensorEntity):
    """Speed walked in the current session."""

    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0.0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._state = self._walking_pad_api.speed / 10
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_speed"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Speed"


class StepsSensor(WalkingPadEntity, SensorEntity):
    """Steps walked in the current session."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True
    _attr_icon = "mdi:walk"

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._state = self._walking_pad_api.steps
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_steps"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Steps"


class StepCadenceSensor(WalkingPadEntity, SensorEntity):
    """Steps cadence in steps per minute."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:walk"
    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0.0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._state = self._walking_pad_api.step_cadence
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_step_cadence"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Step Cadence"


class TotalDistanceSensor(WalkingPadEntity, RestoreSensor):
    """Total Distance walked since HA restart."""

    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    _last = 0

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0.0
        self._last = 0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    async def async_added_to_hass(self) -> None:
        """Restore native_value."""
        await super().async_added_to_hass()
        if (last_sensor_data := await self.async_get_last_sensor_data()) is None:
            return
        self._state = last_sensor_data.native_value

    @callback
    def _handle_coordinator_update(self) -> None:
        val = self._walking_pad_api.distance / 100
        if val is None:
            return

        if self._state is None:
            self._state = val
        elif self._last is not None and val >= self._last:
            self._state = self._state + (val - self._last)
        else:
            self._state = self._state + val

        self._last = val
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_total_distance"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Total Distance"


class TotalTimeSensor(WalkingPadEntity, RestoreSensor):
    """Total Time walked since HA restart."""

    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    _last = 0

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0
        self._last = 0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    async def async_added_to_hass(self) -> None:
        """Restore native_value."""
        await super().async_added_to_hass()
        if (last_sensor_data := await self.async_get_last_sensor_data()) is None:
            return
        self._state = last_sensor_data.native_value

    @callback
    def _handle_coordinator_update(self) -> None:
        val = self._walking_pad_api.time
        if val is None:
            return

        if self._state is None:
            self._state = val
        elif self._last is not None and val >= self._last:
            self._state = self._state + (val - self._last)
        else:
            self._state = self._state + val

        self._last = val
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_total_time"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Total Time"


class TotalStepsSensor(WalkingPadEntity, RestoreSensor):
    """Total Steps walked since HA restart."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True
    _attr_icon = "mdi:walk"

    _last = 0

    def __init__(
        self,
        treadmillName: str,
        walking_pad_api: WalkingPadApi,
        coordinator: WalkingPadCoordinator,
    ) -> None:
        self._state = 0
        self._last = 0
        super().__init__(treadmillName, self.name, walking_pad_api, coordinator)

    async def async_added_to_hass(self) -> None:
        """Restore native_value."""
        await super().async_added_to_hass()
        if (last_sensor_data := await self.async_get_last_sensor_data()) is None:
            return
        self._state = last_sensor_data.native_value

    @callback
    def _handle_coordinator_update(self) -> None:
        val = self._walking_pad_api.steps
        if val is None:
            return

        if self._state is None:
            self._state = val
        elif self._last is not None and val >= self._last:
            self._state = self._state + (val - self._last)
        else:
            self._state = self._state + val

        self._last = val
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._walking_pad_api.mac}_total_steps"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Total Steps"
