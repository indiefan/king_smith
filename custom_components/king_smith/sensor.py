""" Platform sensor integration """
from __future__ import annotations

from homeassistant.components.sensor import ( SensorDeviceClass,
                                             SensorEntity,
                                             SensorStateClass
                                             )
from homeassistant.components.sensor.const import UnitOfTime
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import  CONF_NAME,  UnitOfLength, UnitOfSpeed
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

    entity = DistanceSensor(treadmillName, walking_pad_api, coordinator)
    timeEntity = TimeSensor(treadmillName, walking_pad_api, coordinator)
    speedEntity = SpeedSensor(treadmillName, walking_pad_api, coordinator)
    stepsEntity = StepsSensor(treadmillName, walking_pad_api, coordinator)
    timeTotalEntity = TimeTotalSensor(treadmillName, walking_pad_api, coordinator)
    distanceTotalentity = DistanceTotalSensor(treadmillName, walking_pad_api, coordinator)
    stepsTotalEntity = StepsTotalSensor(treadmillName, walking_pad_api, coordinator)
    
    async_add_entities([entity, timeEntity, speedEntity, stepsEntity, timeTotalEntity, stepsTotalEntity, distanceTotalentity])

class DistanceSensor(WalkingPadEntity, SensorEntity):
    """Session Distance walked in the current session"""

    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = 0.0
        super().__init__(treadmillName, walking_pad_api, coordinator)

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

class DistanceTotalSensor(WalkingPadEntity, SensorEntity):
    """Total Distance walked"""

    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = 0.0
        super().__init__(treadmillName, walking_pad_api, coordinator)

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
        return f"{self._walking_pad_api.mac}_distance_total"
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "Distance Total"

class TimeSensor(WalkingPadEntity, SensorEntity):
    """Session Time walked in the current session"""

    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = None
        super().__init__(treadmillName, walking_pad_api, coordinator)

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

class TimeTotalSensor(WalkingPadEntity, SensorEntity):
    """Total Session Time"""

    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = None
        super().__init__(treadmillName, walking_pad_api, coordinator)

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
        return f"{self._walking_pad_api.mac}_time_total"
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "Time Total"

class SpeedSensor(WalkingPadEntity, SensorEntity):
    """Speed walked in the current session"""

    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = None
        super().__init__(treadmillName, walking_pad_api, coordinator)

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

class StepsSensor(WalkingPadEntity, SensorEntity):
    """Steps walked in the current session"""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = 0
        super().__init__(treadmillName, walking_pad_api, coordinator)

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
    def name(self):
        """Return the name of the sensor."""
        return "Steps"

class StepsTotalSensor(WalkingPadEntity, SensorEntity):
    """Total Steps walked"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_has_entity_name = True

    def __init__(self, treadmillName: str, walking_pad_api: WalkingPadApi, coordinator: WalkingPadCoordinator) -> None:
        self._state = 0
        super().__init__(treadmillName, walking_pad_api, coordinator)

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
        return f"{self._walking_pad_api.mac}_steps_total"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Steps Total"
