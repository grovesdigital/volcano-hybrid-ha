"""Sensor platform for Volcano Hybrid."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import VolcanoCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: VolcanoCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        VolcanoSessionsToday(coordinator),
        VolcanoAverageSessionDuration(coordinator),
        VolcanoFavoriteTemperature(coordinator),
        VolcanoTimeSinceLastUse(coordinator),
        VolcanoTotalRuntimeToday(coordinator),
        VolcanoTargetTemperature(coordinator),
        VolcanoConnectionStatus(coordinator),
    ]
    
    async_add_entities(entities)


class VolcanoSessionsToday(CoordinatorEntity, SensorEntity):
    """Sensor for number of sessions today."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:counter"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_sessions_today"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Sessions Today"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.statistics.get_sessions_today()


class VolcanoAverageSessionDuration(CoordinatorEntity, SensorEntity):
    """Sensor for average session duration."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_avg_session_duration"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Average Session Duration"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return round(self.coordinator.statistics.get_average_session_duration(7), 1)


class VolcanoFavoriteTemperature(CoordinatorEntity, SensorEntity):
    """Sensor for favorite temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer-check"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_favorite_temperature"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Favorite Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.statistics.get_favorite_temperature(30)


class VolcanoTimeSinceLastUse(CoordinatorEntity, SensorEntity):
    """Sensor for time since last use."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-time-eight-outline"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_time_since_last_use"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Time Since Last Use"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        time_delta = self.coordinator.statistics.get_time_since_last_use()
        if time_delta:
            return round(time_delta.total_seconds() / 3600, 1)  # Convert to hours
        return None


class VolcanoTotalRuntimeToday(CoordinatorEntity, SensorEntity):
    """Sensor for total runtime today."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_total_runtime_today"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Total Runtime Today"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return round(self.coordinator.statistics.get_total_runtime_today(), 1)


class VolcanoTargetTemperature(CoordinatorEntity, SensorEntity):
    """Sensor for current target temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_target_temperature"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Target Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("target_temperature")


class VolcanoConnectionStatus(CoordinatorEntity, SensorEntity):
    """Sensor for connection status."""

    _attr_icon = "mdi:bluetooth"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_connection_status"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Connection Status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return "Connected" if self.coordinator.volcano_api.is_connected else "Disconnected"

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:bluetooth-connect" if self.coordinator.volcano_api.is_connected else "mdi:bluetooth-off"
