"""BLE communication layer for Volcano Hybrid."""
from __future__ import annotations

import asyncio
import logging
import struct
from typing import Any, Callable

from bleak import BleakClient
from bleak.exc import BleakError
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth

from ..const import (
    CHAR_BLE_FIRMWARE_VERSION,
    CHAR_CURRENT_TEMP,
    CHAR_FAN_OFF,
    CHAR_FAN_ON,
    CHAR_HEAT_OFF,
    CHAR_HEAT_ON,
    CHAR_HOURS_OF_OPERATION,
    CHAR_MINUTES_OF_OPERATION,
    CHAR_SCREEN_BRIGHTNESS,
    CHAR_SERIAL_NUMBER,
    CHAR_STATUS_REGISTER,
    CHAR_TARGET_TEMP,
    CHAR_VOLCANO_FIRMWARE_VERSION,
)

from .exceptions import VolcanoConnectionError

_LOGGER = logging.getLogger(__name__)


class VolcanoAPI:
    """BLE API for Volcano Hybrid."""

    def __init__(self, hass: HomeAssistant, mac_address: str) -> None:
        """Initialize the Volcano API."""
        self._hass = hass
        self._mac_address = mac_address
        self._client: BleakClient | None = None
        self._is_connected = False
        self._disconnect_callback: Callable[[], None] | None = None
        self._current_temperature = 0.0
        self._target_temperature = 0.0
        self._heat_on = False
        self._fan_on = False

    async def connect(self, max_retries: int = 3) -> bool:
        """Connect to the Volcano device."""
        for attempt in range(max_retries):
            try:
                _LOGGER.debug("Connecting to Volcano at %s (attempt %d/%d)", self._mac_address, attempt + 1, max_retries)
                
                # Use Home Assistant's Bluetooth integration to get BLE device
                ble_device = bluetooth.async_ble_device_from_address(
                    self._hass, self._mac_address.upper(), connectable=True
                )
                if not ble_device:
                    _LOGGER.error("Bluetooth device not found or not connectable: %s", self._mac_address)
                    raise VolcanoConnectionError(f"Device {self._mac_address} not found or not connectable.")

                self._client = BleakClient(
                    ble_device,  # Use BLE device object instead of raw MAC address
                    disconnected_callback=self._handle_disconnect,
                )
                
                await self._client.connect()

                if self._client.is_connected:
                    await self._setup_notifications()
                    self._is_connected = True
                    _LOGGER.info("Successfully connected to Volcano at %s", self._mac_address)
                    return True
                else:
                    _LOGGER.error("Failed to connect to Volcano (attempt %d/%d)", attempt + 1, max_retries)
                    
            except BleakError as err:
                _LOGGER.error("Failed to connect to Volcano (attempt %d/%d): %s", attempt + 1, max_retries, err)
                self._is_connected = False
                if attempt == max_retries - 1:  # Last attempt
                    raise VolcanoConnectionError(f"Failed to connect to Volcano after {max_retries} attempts: {err}") from err
                    
            except Exception as err:
                _LOGGER.error("Unexpected error connecting to Volcano (attempt %d/%d): %s", attempt + 1, max_retries, err)
                self._is_connected = False
                if attempt == max_retries - 1:  # Last attempt
                    raise VolcanoConnectionError(f"Unexpected connection error after {max_retries} attempts: {err}") from err
                    
            # Clean up client on failed attempts
            if self._client:
                try:
                    if self._client.is_connected:
                        await self._client.disconnect()
                except Exception:
                    pass  # Ignore cleanup errors
                finally:
                    self._client = None
                    
            # Wait a bit before retrying
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
                
        return False

    async def disconnect(self) -> None:
        """Disconnect from the Volcano device."""
        try:
            if self._client and self._client.is_connected:
                # Stop notifications before disconnecting
                try:
                    await self._client.stop_notify(CHAR_CURRENT_TEMP)
                    await self._client.stop_notify(CHAR_STATUS_REGISTER)
                except Exception as err:
                    _LOGGER.debug("Error stopping notifications during disconnect: %s", err)
                
                await self._client.disconnect()
                _LOGGER.debug("Disconnected from Volcano")
        except Exception as err:
            _LOGGER.error("Error during disconnect: %s", err)
        finally:
            self._is_connected = False
            self._client = None

    def _handle_disconnect(self, client: BleakClient) -> None:
        """Handle disconnect callback."""
        _LOGGER.info("Volcano disconnected")
        self._is_connected = False
        if self._disconnect_callback:
            self._disconnect_callback()

    def set_disconnect_callback(self, callback: Callable[[], None]) -> None:
        """Set disconnect callback."""
        self._disconnect_callback = callback

    async def _setup_notifications(self) -> None:
        """Setup BLE notifications."""
        if not self._client:
            return

        try:
            # Setup notifications for temperature and status updates
            await self._client.start_notify(CHAR_CURRENT_TEMP, self._handle_temperature_notification)
            await self._client.start_notify(CHAR_STATUS_REGISTER, self._handle_status_notification)
            _LOGGER.debug("Notifications setup successfully")
        except Exception as err:
            _LOGGER.error("Failed to setup notifications: %s", err)
            # Don't raise the error - notifications are optional for basic functionality

    def _handle_temperature_notification(self, sender: int, data: bytearray) -> None:
        """Handle temperature notification."""
        if len(data) >= 2:
            temp = struct.unpack("<H", data[:2])[0] / 10.0
            self._current_temperature = temp
            _LOGGER.debug("Temperature updated: %s°C", temp)

    def _handle_status_notification(self, sender: int, data: bytearray) -> None:
        """Handle status notification."""
        if len(data) >= 1:
            status = data[0]
            self._heat_on = bool(status & 0x01)
            self._fan_on = bool(status & 0x02)
            _LOGGER.debug("Status updated - Heat: %s, Fan: %s", self._heat_on, self._fan_on)

    @property
    def is_connected(self) -> bool:
        """Return if device is connected."""
        return self._is_connected and self._client is not None and self._client.is_connected

    async def get_current_temperature(self) -> float:
        """Get current temperature."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_CURRENT_TEMP)
            temp = struct.unpack("<H", data[:2])[0] / 10.0
            self._current_temperature = temp
            return temp
        except Exception as err:
            _LOGGER.error("Failed to read current temperature: %s", err)
            raise VolcanoConnectionError(f"Failed to read temperature: {err}") from err

    async def get_target_temperature(self) -> float:
        """Get target temperature."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_TARGET_TEMP)
            temp = struct.unpack("<H", data[:2])[0] / 10.0
            self._target_temperature = temp
            return temp
        except Exception as err:
            _LOGGER.error("Failed to read target temperature: %s", err)
            raise VolcanoConnectionError(f"Failed to read target temperature: {err}") from err

    async def set_target_temperature(self, temperature: float) -> None:
        """Set target temperature."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        if not 40 <= temperature <= 230:
            raise ValueError("Temperature must be between 40°C and 230°C")
        
        try:
            temp_value = int(temperature * 10)
            data = struct.pack("<H", temp_value)
            await self._client.write_gatt_char(CHAR_TARGET_TEMP, data)
            self._target_temperature = temperature
            _LOGGER.debug("Target temperature set to %s°C", temperature)
        except Exception as err:
            _LOGGER.error("Failed to set target temperature: %s", err)
            raise VolcanoConnectionError(f"Failed to set temperature: {err}") from err

    async def set_heat_on(self) -> None:
        """Turn heat on."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            await self._client.write_gatt_char(CHAR_HEAT_ON, b"\x01")
            # Immediately read status to confirm change
            await asyncio.sleep(0.1)  # Small delay to let device process
            try:
                status_data = await self._client.read_gatt_char(CHAR_STATUS_REGISTER)
                if len(status_data) >= 1:
                    status = status_data[0]
                    self._heat_on = bool(status & 0x01)
            except Exception:
                # Fall back to optimistic update if status read fails
                self._heat_on = True
            _LOGGER.debug("Heat turned on - Actual state: %s", self._heat_on)
        except Exception as err:
            _LOGGER.error("Failed to turn heat on: %s", err)
            raise VolcanoConnectionError(f"Failed to turn heat on: {err}") from err

    async def set_heat_off(self) -> None:
        """Turn heat off."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            await self._client.write_gatt_char(CHAR_HEAT_OFF, b"\x00")
            # Immediately read status to confirm change
            await asyncio.sleep(0.1)  # Small delay to let device process
            try:
                status_data = await self._client.read_gatt_char(CHAR_STATUS_REGISTER)
                if len(status_data) >= 1:
                    status = status_data[0]
                    self._heat_on = bool(status & 0x01)
            except Exception:
                # Fall back to optimistic update if status read fails
                self._heat_on = False
            _LOGGER.debug("Heat turned off - Actual state: %s", self._heat_on)
        except Exception as err:
            _LOGGER.error("Failed to turn heat off: %s", err)
            raise VolcanoConnectionError(f"Failed to turn heat off: {err}") from err

    async def set_fan_on(self) -> None:
        """Turn fan on."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            await self._client.write_gatt_char(CHAR_FAN_ON, b"\x01")
            # Immediately read status to confirm change
            await asyncio.sleep(0.1)  # Small delay to let device process
            try:
                status_data = await self._client.read_gatt_char(CHAR_STATUS_REGISTER)
                if len(status_data) >= 1:
                    status = status_data[0]
                    self._fan_on = bool(status & 0x02)
            except Exception:
                # Fall back to optimistic update if status read fails
                self._fan_on = True
            _LOGGER.debug("Fan turned on - Actual state: %s", self._fan_on)
        except Exception as err:
            _LOGGER.error("Failed to turn fan on: %s", err)
            raise VolcanoConnectionError(f"Failed to turn fan on: {err}") from err

    async def set_fan_off(self) -> None:
        """Turn fan off."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            await self._client.write_gatt_char(CHAR_FAN_OFF, b"\x00")
            # Immediately read status to confirm change
            await asyncio.sleep(0.1)  # Small delay to let device process
            try:
                status_data = await self._client.read_gatt_char(CHAR_STATUS_REGISTER)
                if len(status_data) >= 1:
                    status = status_data[0]
                    self._fan_on = bool(status & 0x02)
            except Exception:
                # Fall back to optimistic update if status read fails
                self._fan_on = False
            _LOGGER.debug("Fan turned off - Actual state: %s", self._fan_on)
        except Exception as err:
            _LOGGER.error("Failed to turn fan off: %s", err)
            raise VolcanoConnectionError(f"Failed to turn fan off: {err}") from err

    async def set_screen_brightness(self, brightness: int) -> None:
        """Set screen brightness."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be between 0 and 100")
        
        try:
            await self._client.write_gatt_char(CHAR_SCREEN_BRIGHTNESS, bytes([brightness]))
            _LOGGER.debug("Screen brightness set to %s%%", brightness)
        except Exception as err:
            _LOGGER.error("Failed to set screen brightness: %s", err)
            raise VolcanoConnectionError(f"Failed to set brightness: {err}") from err

    async def get_ble_firmware_version(self) -> str:
        """Get BLE firmware version."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_BLE_FIRMWARE_VERSION)
            return data.decode("utf-8").strip()
        except Exception as err:
            _LOGGER.error("Failed to read BLE firmware version: %s", err)
            raise VolcanoConnectionError(f"Failed to read BLE firmware version: {err}") from err

    async def get_volcano_firmware_version(self) -> str:
        """Get Volcano firmware version."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_VOLCANO_FIRMWARE_VERSION)
            return data.decode("utf-8").strip()
        except Exception as err:
            _LOGGER.error("Failed to read Volcano firmware version: %s", err)
            raise VolcanoConnectionError(f"Failed to read Volcano firmware version: {err}") from err

    async def get_serial_number(self) -> str:
        """Get device serial number."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_SERIAL_NUMBER)
            return data.decode("utf-8").strip()
        except Exception as err:
            _LOGGER.error("Failed to read serial number: %s", err)
            raise VolcanoConnectionError(f"Failed to read serial number: {err}") from err

    async def get_hours_of_operation(self) -> int:
        """Get hours of operation."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_HOURS_OF_OPERATION)
            return struct.unpack("<H", data[:2])[0]
        except Exception as err:
            _LOGGER.error("Failed to read hours of operation: %s", err)
            raise VolcanoConnectionError(f"Failed to read hours of operation: {err}") from err

    async def get_minutes_of_operation(self) -> int:
        """Get minutes of operation."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            data = await self._client.read_gatt_char(CHAR_MINUTES_OF_OPERATION)
            return struct.unpack("<H", data[:2])[0]
        except Exception as err:
            _LOGGER.error("Failed to read minutes of operation: %s", err)
            raise VolcanoConnectionError(f"Failed to read minutes of operation: {err}") from err

    async def get_device_state(self) -> dict[str, Any]:
        """Get current device state by reading from device."""
        if not self.is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        try:
            # Read the status register to get real-time heat/fan state
            status_data = await self._client.read_gatt_char(CHAR_STATUS_REGISTER)
            if len(status_data) >= 1:
                status = status_data[0]
                # Update cached states with fresh data
                self._heat_on = bool(status & 0x01)
                self._fan_on = bool(status & 0x02)
                _LOGGER.debug("Status register read - Heat: %s, Fan: %s", self._heat_on, self._fan_on)
        except Exception as err:
            _LOGGER.error("Failed to read status register: %s", err)
            # Fall back to cached state if read fails
        
        return {
            "current_temperature": self._current_temperature,
            "target_temperature": self._target_temperature,
            "heat_on": self._heat_on,
            "fan_on": self._fan_on,
            "connected": self._is_connected,
        }

    # Current state properties
    @property
    def current_temperature(self) -> float:
        """Current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self) -> float:
        """Target temperature."""
        return self._target_temperature

    @property
    def heat_on(self) -> bool:
        """Heat status."""
        return self._heat_on

    @property
    def fan_on(self) -> bool:
        """Fan status."""
        return self._fan_on
