"""BLE communication layer for Volcano Hybrid."""
from __future__ import annotations

import asyncio
import logging
import struct
from typing import Any, Callable

from bleak import BleakClient  # Keep this
from bleak.exc import BleakError
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth  # ADDED import

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

# Status register bit masks
STATUS_FAN_ON_MASK = 0x2000
STATUS_HEAT_ON_MASK = 0x0020

_LOGGER = logging.getLogger(__name__)


class VolcanoAPI:
    """BLE API for Volcano Hybrid device."""

    def __init__(self, hass: HomeAssistant, mac_address: str) -> None:
        """Initialize the API."""
        self._hass = hass
        self._mac_address = mac_address
        self._client: BleakClient | None = None  # UPDATED type hint
        self._notification_callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._is_connected = False
        self._current_state = {
            "heat_on": False,
            "fan_on": False,
            "target_temperature": None,
            "current_temperature": None,
        }

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._is_connected

    @property
    def mac_address(self) -> str:
        """Return MAC address."""
        return self._mac_address

    @property
    def current_state(self) -> dict[str, Any]:
        """Return current device state."""
        return self._current_state.copy()

    def add_notification_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Add callback for state changes."""
        self._notification_callbacks.append(callback)

    def remove_notification_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Remove callback for state changes."""
        if callback in self._notification_callbacks:
            self._notification_callbacks.remove(callback)

    async def connect(self) -> bool:
        """Connect to the Volcano device."""
        try:
            _LOGGER.debug("Connecting to Volcano at %s", self._mac_address)
            
            ble_device = bluetooth.async_ble_device_from_address(
                self._hass, self._mac_address.upper(), connectable=True
            )
            if not ble_device:
                _LOGGER.error(f"Bluetooth device not found or not connectable: {self._mac_address}")
                raise VolcanoConnectionError(f"Device {self._mac_address} not found or not connectable.")

            self._client = BleakClient(
                ble_device,
                disconnected_callback=self._handle_disconnect,
            )
            
            await self._client.connect() # Explicitly connect

            if self._client.is_connected:
                await self._setup_notifications()
                self._is_connected = True
                _LOGGER.info("Successfully connected to Volcano at %s", self._mac_address)
                return True
            else:
                # This path should ideally not be reached if connect() raises on failure
                _LOGGER.error("Failed to connect to Volcano after BleakClient instantiation")
                if self._client: # Ensure client is cleaned up
                    try:
                        await self._client.disconnect()
                    except Exception: # nosec B110
                        pass # Ignore errors during cleanup here
                    self._client = None
                return False
                
        except BleakError as err:
            _LOGGER.error("BleakError connecting to %s: %s", self._mac_address, err)
            if self._client: # Ensure client is cleaned up
                try:
                    if self._client.is_connected:
                        await self._client.disconnect()
                except BleakError as e_disc:
                     _LOGGER.debug(f"BleakError during cleanup disconnect: {e_disc}")
                except Exception as e_generic_disc:
                    _LOGGER.debug(f"Generic error during cleanup disconnect: {e_generic_disc}")
                finally:
                    self._client = None
            self._is_connected = False
            raise VolcanoConnectionError(f"Failed to connect to Volcano {self._mac_address}: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error during connection to %s: %s", self._mac_address, err)
            if self._client: # Ensure client is cleaned up
                try:
                    if self._client.is_connected:
                        await self._client.disconnect()
                except Exception as e_cleanup:
                     _LOGGER.debug(f"Error during cleanup on unexpected error: {e_cleanup}")
                finally:
                    self._client = None
            self._is_connected = False
            raise VolcanoConnectionError(f"Unexpected connection error for {self._mac_address}: {err}") from err

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client and self._is_connected:
            try:
                await self._client.stop_notify(CHAR_STATUS_REGISTER)
                await self._client.disconnect()
            except Exception as err:
                _LOGGER.error("Error during disconnect: %s", err)
            finally:
                self._is_connected = False
                self._client = None
                _LOGGER.info("Disconnected from Volcano")

    async def _setup_notifications(self) -> None:
        """Setup BLE notifications."""
        if not self._client:
            return

        try:
            # Read initial state
            value = await self._client.read_gatt_char(CHAR_STATUS_REGISTER)
            self._handle_status_notification(CHAR_STATUS_REGISTER, value)
            
            # Start notifications
            await self._client.start_notify(CHAR_STATUS_REGISTER, self._handle_status_notification)
            _LOGGER.debug("Notifications setup successfully")
            
        except Exception as err:
            _LOGGER.error("Failed to setup notifications: %s", err)

    def _handle_disconnect(self, client: BleakClient) -> None:
        """Handle disconnection."""
        _LOGGER.warning("Volcano device disconnected")
        self._is_connected = False
        self._client = None

    def _handle_status_notification(self, sender: str, data: bytes) -> None:
        """Handle status notification from device."""
        try:
            decoded_value = data[0] + (data[1] * 256)
            fan_on = bool(decoded_value & STATUS_FAN_ON_MASK)
            heat_on = bool(decoded_value & STATUS_HEAT_ON_MASK)
            
            old_state = self._current_state.copy()
            self._current_state.update({
                "fan_on": fan_on,
                "heat_on": heat_on,
            })
            
            # Notify callbacks if state changed
            if old_state != self._current_state:
                for callback in self._notification_callbacks:
                    try:
                        callback(self._current_state.copy())
                    except Exception as err:
                        _LOGGER.error("Error in notification callback: %s", err)
                        
            _LOGGER.debug("Status update - Heat: %s, Fan: %s", heat_on, fan_on)
            
        except Exception as err:
            _LOGGER.error("Error processing status notification: %s", err)

    async def _write_characteristic(self, uuid: str, data: bytes) -> bool:
        """Write to a characteristic with error handling."""
        if not self._client or not self._is_connected:
            raise VolcanoConnectionError("Device not connected")

        try:
            await self._client.write_gatt_char(uuid, data)
            return True
        except BleakError as err:
            _LOGGER.error("BLE write error for %s: %s", uuid, err)
            raise VolcanoConnectionError(f"Write failed: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected write error for %s: %s", uuid, err)
            raise VolcanoConnectionError(f"Write error: {err}") from err

    async def set_heat_on(self) -> bool:
        """Turn heat on."""
        result = await self._write_characteristic(CHAR_HEAT_ON, bytes([0]))
        if result:
            self._current_state["heat_on"] = True
        return result

    async def set_heat_off(self) -> bool:
        """Turn heat off."""
        result = await self._write_characteristic(CHAR_HEAT_OFF, bytes([0]))
        if result:
            self._current_state["heat_on"] = False
        return result

    async def set_fan_on(self) -> bool:
        """Turn fan on."""
        result = await self._write_characteristic(CHAR_FAN_ON, bytes([0]))
        if result:
            self._current_state["fan_on"] = True
        return result

    async def set_fan_off(self) -> bool:
        """Turn fan off."""
        result = await self._write_characteristic(CHAR_FAN_OFF, bytes([0]))
        if result:
            self._current_state["fan_on"] = False
        return result

    async def set_target_temperature(self, temperature_celsius: int) -> bool:
        """Set target temperature in Celsius."""
        if not 40 <= temperature_celsius <= 230:
            raise ValueError(f"Temperature {temperature_celsius}°C out of range (40-230°C)")
            
        temp_data = struct.pack('<I', temperature_celsius * 10)
        result = await self._write_characteristic(CHAR_TARGET_TEMP, temp_data)
        if result:
            self._current_state["target_temperature"] = temperature_celsius
        return result

    async def get_target_temperature(self) -> int | None:
        """Get current target temperature."""
        if not self._client or not self._is_connected:
            # Try to reconnect if not connected
            if not await self.connect():
                return None

        try:
            value = await self._client.read_gatt_char(CHAR_TARGET_TEMP)
            decoded_value = value[0] + (value[1] * 256)
            temp = round(decoded_value / 10)
            self._current_state["target_temperature"] = temp
            return temp
        except Exception as err:
            _LOGGER.error("Error reading target temperature: %s", err)
            # Mark as disconnected and try to reconnect on next call
            self._is_connected = False
            return None

    async def set_screen_brightness(self, brightness: int) -> bool:
        """Set screen brightness (0-100)."""
        if not 0 <= brightness <= 100:
            raise ValueError(f"Brightness {brightness} out of range (0-100)")
            
        brightness_data = struct.pack('<H', brightness)
        return await self._write_characteristic(CHAR_SCREEN_BRIGHTNESS, brightness_data)

    async def get_device_state(self) -> dict[str, Any]:
        """Get current device state."""
        if not self._client or not self._is_connected:
            raise VolcanoConnectionError("Device not connected")
        
        # Update target temperature
        await self.get_target_temperature()
        
        return self._current_state.copy()

    async def next_temperature_preset(self) -> bool:
        """Cycle to next temperature preset."""
        current_temp = await self.get_target_temperature()
        if current_temp is None:
            current_temp = 185
            
        # Cycle through presets: 185 -> 190 -> 195 -> 200 -> 185
        next_temp = current_temp + 5
        if next_temp not in (185, 190, 195, 200):
            next_temp = 185
            
        await self.set_target_temperature(next_temp)
        return await self.set_heat_on()

    async def get_current_temperature(self) -> int | None:
        """Get current actual temperature."""
        if not self._client or not self._is_connected:
            # Try to reconnect if not connected
            if not await self.connect():
                return None

        try:
            value = await self._client.read_gatt_char(CHAR_CURRENT_TEMP)
            decoded_value = value[0] + (value[1] * 256)
            temp = round(decoded_value / 10)
            self._current_state["current_temperature"] = temp
            return temp
        except Exception as err:
            _LOGGER.error("Error reading current temperature: %s", err)
            # Mark as disconnected and try to reconnect on next call
            self._is_connected = False
            return None

    async def get_ble_firmware_version(self) -> str | None:
        """Get BLE firmware version."""
        if not self._client or not self._is_connected:
            return None
        
        try:
            value = await self._client.read_gatt_char(CHAR_BLE_FIRMWARE_VERSION)
            # Convert bytes to string, typically UTF-8 encoded
            version = value.decode('utf-8').strip('\x00')
            return version
        except Exception as err:
            _LOGGER.error("Error reading BLE firmware version: %s", err)
            return None
    
    async def get_volcano_firmware_version(self) -> str | None:
        """Get Volcano firmware version."""
        if not self._client or not self._is_connected:
            return None
        
        try:
            value = await self._client.read_gatt_char(CHAR_VOLCANO_FIRMWARE_VERSION)
            # Convert bytes to string, typically UTF-8 encoded
            version = value.decode('utf-8').strip('\x00')
            return version
        except Exception as err:
            _LOGGER.error("Error reading Volcano firmware version: %s", err)
            return None
    
    async def get_serial_number(self) -> str | None:
        """Get device serial number."""
        if not self._client or not self._is_connected:
            return None
        
        try:
            value = await self._client.read_gatt_char(CHAR_SERIAL_NUMBER)
            # Convert bytes to string
            serial = value.decode('utf-8').strip('\x00')
            return serial
        except Exception as err:
            _LOGGER.error("Error reading serial number: %s", err)
            return None
    
    async def get_hours_of_operation(self) -> int | None:
        """Get total hours of operation."""
        if not self._client or not self._is_connected:
            return None
        
        try:
            value = await self._client.read_gatt_char(CHAR_HOURS_OF_OPERATION)
            if len(value) >= 2:
                # Assume little-endian 16-bit integer
                hours = int.from_bytes(value[:2], byteorder='little')
                return hours
            elif len(value) >= 4:
                # Or it might be 32-bit integer
                hours = int.from_bytes(value[:4], byteorder='little')
                return hours
        except Exception as err:
            _LOGGER.error("Error reading hours of operation: %s", err)
            return None
    
    async def get_minutes_of_operation(self) -> int | None:
        """Get total minutes of operation."""
        if not self._client or not self._is_connected:
            return None
        
        try:
            value = await self._client.read_gatt_char(CHAR_MINUTES_OF_OPERATION)
            if len(value) >= 2:
                # Assume little-endian 16-bit integer
                minutes = int.from_bytes(value[:2], byteorder='little')
                return minutes
            elif len(value) >= 4:
                # Or it might be 32-bit integer
                minutes = int.from_bytes(value[:4], byteorder='little')
                return minutes
        except Exception as err:
            _LOGGER.error("Error reading minutes of operation: %s", err)
            return None
