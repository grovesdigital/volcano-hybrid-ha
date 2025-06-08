"""The Volcano Hybrid integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CHAR_BLE_FIRMWARE_VERSION,
    CHAR_CURRENT_TEMP,
    CHAR_HOURS_OF_OPERATION,
    CHAR_MINUTES_OF_OPERATION,
    CHAR_SERIAL_NUMBER,
    CHAR_TARGET_TEMP,
    CHAR_VOLCANO_FIRMWARE_VERSION,
    CONF_MAC_ADDRESS,
    DOMAIN,
    PLATFORMS,
)
from .volcano.api import VolcanoAPI
from .volcano.exceptions import VolcanoConnectionError

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Volcano Hybrid from a config entry."""
    _LOGGER.debug("Setting up Volcano Hybrid integration")
    
    mac_address = entry.data[CONF_MAC_ADDRESS]
    
    coordinator = VolcanoCoordinator(hass, mac_address, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady as err:
        await coordinator.volcano_api.disconnect()
        raise err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Volcano Hybrid integration")
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.volcano_api.disconnect()

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

class VolcanoCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Volcano device."""

    def __init__(self, hass: HomeAssistant, mac_address: str, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),  # Increased from 30 to 60 seconds
        )
        self.volcano_api = VolcanoAPI(hass, mac_address)
        self.config_entry = config_entry
        self._mac_address = mac_address

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._mac_address)},
            "name": "Volcano Hybrid",
            "manufacturer": "Storz & Bickel",
            "model": "Volcano Hybrid",
            "sw_version": "1.0",
        }

    async def get_current_temperature(self) -> int | None:
        """Get current actual temperature from device."""
        try:
            return await self.volcano_api.get_current_temperature()
        except Exception as err:
            _LOGGER.error("Error reading current temperature: %s", err)
            return None

    async def get_device_info_data(self) -> dict[str, Any]:
        """Get device information data."""
        try:
            info_data = {}
            
            # Get firmware versions
            ble_fw = await self.volcano_api.get_ble_firmware_version()
            if ble_fw:
                info_data["ble_firmware_version"] = ble_fw
                
            volcano_fw = await self.volcano_api.get_volcano_firmware_version()
            if volcano_fw:
                info_data["volcano_firmware_version"] = volcano_fw
                
            # Get serial number
            serial = await self.volcano_api.get_serial_number()
            if serial:
                info_data["serial_number"] = serial
                
            # Get operation hours and minutes
            hours = await self.volcano_api.get_hours_of_operation()
            if hours is not None:
                info_data["hours_of_operation"] = hours
                
            minutes = await self.volcano_api.get_minutes_of_operation()
            if minutes is not None:
                info_data["minutes_of_operation"] = minutes
                
            return info_data
        except Exception as err:
            _LOGGER.error("Error reading device info: %s", err)
            return {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            data = {}
            
            # FAST UPDATE (every 5 seconds) - Temperature sensors
            current_temp = await self.get_current_temperature()
            if current_temp is not None:
                data["current_temperature"] = current_temp
            
            target_temp = await self.volcano_api.get_target_temperature()
            if target_temp is not None:
                data["target_temperature"] = target_temp
            
            # Get device status (connection status)
            status = await self.volcano_api.get_device_state()
            if status is not None:
                data.update(status)
        
            # SLOW UPDATE (every 10 minutes) - Device info sensors
            # Initialize counter if not exists
            if not hasattr(self, '_device_info_counter'):
                self._device_info_counter = 0
            
            # Update device info every 120 cycles (120 * 5 seconds = 10 minutes)
            if self._device_info_counter % 120 == 0:  
                device_info = await self.get_device_info_data()
                if device_info:
                    # Cache the device info for persistence
                    self._cached_device_info = device_info
                    data.update(device_info)
            else:
                # Use cached device info between slow updates
                if hasattr(self, '_cached_device_info'):
                    data.update(self._cached_device_info)
                
            self._device_info_counter += 1
            
            return data
        except Exception as err:
            _LOGGER.error("Unexpected error updating data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
