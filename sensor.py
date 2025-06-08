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
        VolcanoTargetTemperature(coordinator),
        VolcanoCurrentTemperature(coordinator),
        VolcanoConnectionStatus(coordinator),
        VolcanoBLEFirmwareVersion(coordinator),
        VolcanoFirmwareVersion(coordinator),
        VolcanoSerialNumber(coordinator),
        VolcanoHoursOfOperation(coordinator),
        VolcanoMinutesOfOperation(coordinator),
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


class VolcanoHoursOfOperation(CoordinatorEntity, SensorEntity):
    """Sensor for total hours of operation."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:clock-time-eight"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_hours_of_operation"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Hours of Operation"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("hours_of_operation")


class VolcanoMinutesOfOperation(CoordinatorEntity, SensorEntity):
    """Sensor for total minutes of operation."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_minutes_of_operation"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Minutes of Operation"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("minutes_of_operation")
