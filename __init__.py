"""The Volcano Hybrid integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
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
        # Dynamic update intervals
        self._base_update_interval = 5  # 5 seconds when idle
        self._active_update_interval = 2  # 2 seconds when heating
        self._fast_update_interval = 1   # 1 second when fan is on
        
        # Initialize with base interval
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self._base_update_interval),
        )
        self.volcano_api = VolcanoAPI(hass, mac_address)
        self.config_entry = config_entry
        self._mac_address = mac_address
        
        # Session tracking
        self._session_start_time: datetime | None = None
        self._last_session_end_time: datetime | None = None
        self._session_durations: list[float] = []
        self._sessions_today: int = 0
        self._total_sessions: int = 0
        self._last_reset_date = datetime.now().date()
        
        # Temperature tracking for events
        self._last_temp: int | None = None
        self._last_target_temp: int | None = None
        self._last_fan_state: bool = False

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

    def _reset_daily_stats(self) -> None:
        """Reset daily statistics if it's a new day."""
        today = datetime.now().date()
        if today != self._last_reset_date:
            self._sessions_today = 0
            self._last_reset_date = today

    def _detect_session_start(self, current_temp: int, target_temp: int) -> None:
        """Detect session start and fire event."""
        # Session starts when temp goes from low to heating up with a target set
        if (self._last_temp is not None and 
            self._last_temp < 50 and 
            current_temp > 60 and 
            target_temp > 100 and
            self._session_start_time is None):
            
            self._session_start_time = datetime.now()
            self._sessions_today += 1
            self._total_sessions += 1
            
            self.hass.bus.async_fire("volcano_session_event", {
                "type": "session_started",
                "target_temperature": target_temp,
                "current_temperature": current_temp,
                "timestamp": self._session_start_time.isoformat(),
                "session_count_today": self._sessions_today,
                "total_sessions": self._total_sessions,
            })
            _LOGGER.debug("Session started - Target: %s°C", target_temp)

    def _detect_temperature_reached(self, current_temp: int, target_temp: int) -> None:
        """Detect when target temperature is reached."""
        if (target_temp and current_temp >= (target_temp - 5) and 
            self._last_temp is not None and 
            self._last_temp < (target_temp - 5)):
            
            self.hass.bus.async_fire("volcano_session_event", {
                "type": "temperature_reached",
                "target_temperature": target_temp,
                "actual_temperature": current_temp,
                "timestamp": datetime.now().isoformat(),
                "session_active": self._session_start_time is not None,
            })
            _LOGGER.debug("Target temperature reached - %s°C", current_temp)

    def _detect_session_end(self, current_temp: int, fan_on: bool) -> None:
        """Detect session end and calculate duration."""
        # Session ends when temp drops significantly or manual shutdown
        session_ending = (
            (current_temp < 50 and self._last_temp and self._last_temp > 80) or
            (not fan_on and self._last_fan_state and current_temp > 100)
        )
        
        if session_ending and self._session_start_time is not None:
            session_end_time = datetime.now()
            duration = (session_end_time - self._session_start_time).total_seconds() / 60  # minutes
            
            self._session_durations.append(duration)
            # Keep only last 100 sessions for average calculation
            if len(self._session_durations) > 100:
                self._session_durations.pop(0)
            
            self._last_session_end_time = session_end_time
            
            self.hass.bus.async_fire("volcano_session_event", {
                "type": "session_ended",
                "duration_minutes": round(duration, 1),
                "start_time": self._session_start_time.isoformat(),
                "end_time": session_end_time.isoformat(),
                "timestamp": session_end_time.isoformat(),
            })
            
            self._session_start_time = None
            _LOGGER.debug("Session ended - Duration: %.1f minutes", duration)

    def _handle_fan_events(self, fan_on: bool) -> None:
        """Handle fan state changes and fire events."""
        if fan_on != self._last_fan_state:
            if fan_on:
                self.hass.bus.async_fire("volcano_session_event", {
                    "type": "fan_started",
                    "timestamp": datetime.now().isoformat(),
                    "session_active": self._session_start_time is not None,
                })
                _LOGGER.debug("Fan started")
            else:
                self.hass.bus.async_fire("volcano_session_event", {
                    "type": "fan_stopped",
                    "timestamp": datetime.now().isoformat(),
                    "session_active": self._session_start_time is not None,
                })
                _LOGGER.debug("Fan stopped")

    @property
    def sessions_today(self) -> int:
        """Get sessions count for today."""
        self._reset_daily_stats()
        return self._sessions_today

    @property
    def total_sessions(self) -> int:
        """Get total sessions count."""
        return self._total_sessions

    @property
    def average_session_duration(self) -> float | None:
        """Get average session duration in minutes."""
        if not self._session_durations:
            return None
        return round(sum(self._session_durations) / len(self._session_durations), 1)

    @property
    def last_session_duration(self) -> float | None:
        """Get last session duration in minutes."""
        return self._session_durations[-1] if self._session_durations else None

    @property
    def time_since_last_use(self) -> int | None:
        """Get minutes since last session ended."""
        if self._last_session_end_time is None:
            return None
        return int((datetime.now() - self._last_session_end_time).total_seconds() / 60)

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

    def _get_dynamic_update_interval(self) -> int:
        """Get update interval based on device state."""
        heat_on = self.data.get("heat_on", False) if self.data else False
        fan_on = self.data.get("fan_on", False) if self.data else False
        current_temp = self.data.get("current_temperature", 0) if self.data else 0
        target_temp = self.data.get("target_temperature", 0) if self.data else 0
        
        # Fast updates during fan operation (balloon sessions need real-time feedback)
        if fan_on:
            return self._fast_update_interval  # 1 second when fan is on
        
        # Active updates when heating and approaching target (last 10°C)
        if heat_on and target_temp > 0 and current_temp > (target_temp - 10):
            return self._fast_update_interval  # 1 second when close to target
        
        # Active updates when heating
        if heat_on or (target_temp > 0 and current_temp < target_temp):
            return self._active_update_interval  # 2 seconds when actively heating
        
        # Slower when cooling down but still warm
        if current_temp > 50:
            return 3  # 3 seconds when cooling
        
        # Normal updates when completely idle
        return self._base_update_interval  # 5 seconds when cold/idle

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            data = {}
            
            # Try to reconnect if not connected
            if not self.volcano_api.is_connected:
                _LOGGER.debug("Device not connected, attempting to reconnect...")
                try:
                    await self.volcano_api.connect(max_retries=2)
                except VolcanoConnectionError as err:
                    _LOGGER.warning("Failed to reconnect to device: %s", err)
                    # Return minimal data indicating disconnection
                    return {
                        "connected": False,
                        "current_temperature": None,
                        "target_temperature": None,
                        "heat_on": False,
                        "fan_on": False,
                    }
            
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
            
            # Session tracking and event firing
            fan_on = status.get("fan_on", False) if status else False
            
            if current_temp is not None and target_temp is not None:
                self._detect_session_start(current_temp, target_temp)
                self._detect_temperature_reached(current_temp, target_temp)
                self._detect_session_end(current_temp, fan_on)
            
            if status:
                self._handle_fan_events(fan_on)
            
            # Update tracking variables
            self._last_temp = current_temp
            self._last_target_temp = target_temp
            self._last_fan_state = fan_on
            
            # Add session statistics to data
            data.update({
                "sessions_today": self.sessions_today,
                "total_sessions": self.total_sessions,
                "last_session_duration": self.last_session_duration,
                "average_session_duration": self.average_session_duration,
                "time_since_last_use": self.time_since_last_use,
            })
            
            # Add session statistics to data
            data["sessions_today"] = self.sessions_today
            data["total_sessions"] = self.total_sessions
            data["average_session_duration"] = self.average_session_duration
            data["last_session_duration"] = self.last_session_duration
            data["time_since_last_use"] = self.time_since_last_use
        
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
            
            # After getting all data, adjust update interval dynamically
            new_interval = self._get_dynamic_update_interval()
            if new_interval != self.update_interval.total_seconds():
                self.update_interval = timedelta(seconds=new_interval)
                _LOGGER.debug("Update interval changed to %s seconds", new_interval)
            
            return data
        except VolcanoConnectionError as err:
            _LOGGER.warning("Connection error updating data: %s", err)
            # Return disconnected state instead of failing
            return {
                "connected": False,
                "current_temperature": None,
                "target_temperature": None,
                "heat_on": False,
                "fan_on": False,
            }
        except Exception as err:
            _LOGGER.error("Unexpected error updating data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
