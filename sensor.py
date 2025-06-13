"""Sensor platform for Volcano Hybrid."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

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
        # Temperature sensors
        VolcanoTargetTemperature(coordinator),
        VolcanoCurrentTemperature(coordinator),
        
        # Connection and device info
        VolcanoConnectionStatus(coordinator),
        VolcanoHeatStatusSensor(coordinator),  # NEW
        VolcanoFanStatusSensor(coordinator),   # NEW
        VolcanoBLEFirmwareVersion(coordinator),
        VolcanoFirmwareVersion(coordinator),
        VolcanoSerialNumber(coordinator),
        VolcanoTotalOperationTime(coordinator),
        
        # Session tracking statistics
        VolcanoSessionsTodaySensor(coordinator),
        VolcanoTotalSessionsSensor(coordinator),
        VolcanoLastSessionDurationSensor(coordinator),
        VolcanoAverageSessionDurationSensor(coordinator),
        VolcanoTimeSinceLastUseSensor(coordinator),
    ]
    
    async_add_entities(entities)


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


class VolcanoCurrentTemperature(CoordinatorEntity, SensorEntity):
    """Sensor for current actual temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_current_temperature"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Current Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("current_temperature")


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


class VolcanoBLEFirmwareVersion(CoordinatorEntity, SensorEntity):
    """Sensor for BLE firmware version."""

    _attr_icon = "mdi:chip"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_ble_firmware_version"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano BLE Firmware Version"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("ble_firmware_version")


class VolcanoFirmwareVersion(CoordinatorEntity, SensorEntity):
    """Sensor for Volcano firmware version."""

    _attr_icon = "mdi:chip"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_volcano_firmware_version"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Firmware Version"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("volcano_firmware_version")


class VolcanoSerialNumber(CoordinatorEntity, SensorEntity):
    """Sensor for device serial number."""

    _attr_icon = "mdi:barcode"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_serial_number"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Serial Number"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("serial_number")


class VolcanoTotalOperationTime(CoordinatorEntity, SensorEntity):
    """Sensor for total operation time in days:hours:minutes format."""

    _attr_icon = "mdi:clock-time-eight"
    _attr_native_unit_of_measurement = None  # Custom format

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_total_operation_time"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Total Operation Time"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor in days:hours:minutes format."""
        hours = self.coordinator.data.get("hours_of_operation", 0)
        minutes = self.coordinator.data.get("minutes_of_operation", 0)
        
        if hours is None and minutes is None:
            return None
        
        # Convert to total minutes
        total_minutes = (hours or 0) * 60 + (minutes or 0)
        
        # Calculate days, hours, and remaining minutes
        days = total_minutes // (24 * 60)
        remaining_minutes = total_minutes % (24 * 60)
        hours_part = remaining_minutes // 60
        minutes_part = remaining_minutes % 60
        
        return f"{days}d {hours_part}h {minutes_part}m"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        hours = self.coordinator.data.get("hours_of_operation", 0)
        minutes = self.coordinator.data.get("minutes_of_operation", 0)
        
        if hours is None and minutes is None:
            return {}
        
        total_minutes = (hours or 0) * 60 + (minutes or 0)
        total_hours = total_minutes / 60
        days = total_minutes // (24 * 60)
        
        return {
            "total_hours": round(total_hours, 1),
            "total_minutes": total_minutes,
            "days": days,
            "raw_hours": hours or 0,
            "raw_minutes": minutes or 0,
        }


class VolcanoSessionsTodaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for sessions count today."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "sessions"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_sessions_today"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Sessions Today"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("sessions_today")


class VolcanoTotalSessionsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total sessions count."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "sessions"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_total_sessions"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Total Sessions"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("total_sessions")


class VolcanoLastSessionDurationSensor(CoordinatorEntity, SensorEntity):
    """Sensor for last session duration."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:timer"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_last_session_duration"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Last Session Duration"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("last_session_duration")


class VolcanoAverageSessionDurationSensor(CoordinatorEntity, SensorEntity):
    """Sensor for average session duration."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_average_session_duration"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Average Session Duration"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("average_session_duration")


class VolcanoTimeSinceLastUseSensor(CoordinatorEntity, SensorEntity):
    """Sensor for time since last use."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_time_since_last_use"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Time Since Last Use"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("time_since_last_use")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        time_since = self.coordinator.data.get("time_since_last_use")
        if time_since is None:
            return None
        
        # Convert minutes to human readable format
        hours = time_since // 60
        minutes = time_since % 60
        
        if hours > 0:
            readable = f"{hours}h {minutes}m"
        else:
            readable = f"{minutes}m"
            
        return {
            "readable_time": readable,
            "hours": hours,
            "minutes_remainder": minutes,
        }


class VolcanoHeatStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for heat status."""

    _attr_icon = "mdi:heating-coil"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_heat_status"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Heat Status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return "On" if self.coordinator.data.get("heat_on", False) else "Off"

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:fire" if self.coordinator.data.get("heat_on", False) else "mdi:fire-off"


class VolcanoFanStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for fan status."""

    _attr_icon = "mdi:fan"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_fan_status"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Fan Status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return "On" if self.coordinator.data.get("fan_on", False) else "Off"

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:fan" if self.coordinator.data.get("fan_on", False) else "mdi:fan-off"
