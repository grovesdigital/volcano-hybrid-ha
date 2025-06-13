"""Config flow for Volcano Hybrid integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from bleak import BleakScanner

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_MAC_ADDRESS, DOMAIN, VOLCANO_SERVICE_UUID
from .volcano.api import VolcanoAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_MAC_ADDRESS): str,
})

STEP_DISCOVERY_DATA_SCHEMA = vol.Schema({
    vol.Required("action"): vol.In(["scan", "manual"]),
})


class VolcanoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Volcano Hybrid."""
    
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_device: BluetoothServiceInfoBleak | None = None
        self._mac_address: str | None = None
        self._discovered_devices: list[dict[str, str]] = []

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug("Bluetooth discovery: %s", discovery_info)
        
        # Check if this is a Volcano device
        if not self._is_volcano_device(discovery_info):
            return self.async_abort(reason="not_supported")

        # Normalize MAC address format
        formatted_mac = discovery_info.address.upper().replace(":", "").replace("-", "")
        formatted_mac = ":".join([formatted_mac[i:i+2] for i in range(0, 12, 2)])

        await self.async_set_unique_id(formatted_mac)
        
        # Check if there's an active config entry (not just entities in registry)
        existing_entries = [
            entry for entry in self._async_current_entries()
            if entry.data.get(CONF_MAC_ADDRESS) == formatted_mac
        ]
        
        if existing_entries:
            _LOGGER.debug("Device %s already has active config entry, ignoring discovery", formatted_mac)
            return self.async_abort(reason="already_configured")
        
        # If we reach here, entities might exist but no active config entry
        # This is fine - we can adopt the existing entities
        _LOGGER.debug("Device %s will be configured (may adopt existing entities)", formatted_mac)
        
        self._discovered_device = discovery_info
        self._mac_address = formatted_mac
        # Create entry without testing connection (will be tested during setup)
        return self.async_create_entry(
            title=f"Volcano Hybrid ({formatted_mac})",
            data={CONF_MAC_ADDRESS: formatted_mac}
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step with discovery option."""
        if user_input is not None:
            if user_input["action"] == "scan":
                return await self.async_step_discovery()
            elif user_input["action"] == "manual":
                return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_DISCOVERY_DATA_SCHEMA,
            description_placeholders={
                "description": "Choose to scan for Volcano devices automatically or enter MAC address manually"
            }
        )

    async def async_step_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle scanning for Volcano devices."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            if "device" in user_input:
                # User selected a device from the scan results
                selected_display = user_input["device"]
                selected_device = None
                for device in self._discovered_devices:
                    if device["display"] == selected_display:
                        selected_device = device
                        break
                
                if selected_device:
                    mac_address = selected_device["address"]
                    formatted_mac = mac_address.upper().replace(":", "").replace("-", "")
                    formatted_mac = ":".join([formatted_mac[i:i+2] for i in range(0, 12, 2)])
                    
                    try:
                        await self.async_set_unique_id(formatted_mac)
                        
                        # Check for existing active config entries, not just entity registry
                        existing_entries = [
                            entry for entry in self._async_current_entries()
                            if entry.data.get(CONF_MAC_ADDRESS) == formatted_mac
                        ]
                        
                        if existing_entries:
                            errors["base"] = "already_configured"
                        elif await self._test_connection(formatted_mac):
                            return self.async_create_entry(
                                title=f"Volcano Hybrid ({formatted_mac})",
                                data={CONF_MAC_ADDRESS: formatted_mac}
                            )
                        else:
                            errors["base"] = "cannot_connect"
                    except Exception as err:
                        _LOGGER.exception("Error during device setup: %s", err)
                        errors["base"] = "unknown"
            else:
                errors["base"] = "no_device_selected"
        
        # Scan for devices
        self._discovered_devices = await self._scan_for_volcano_devices()
        
        if not self._discovered_devices:
            errors["base"] = "no_devices_found"
            # Return to user step to try manual entry
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_DISCOVERY_DATA_SCHEMA,
                errors={"base": "no_devices_found"}
            )
        
        return self.async_show_form(
            step_id="discovery",
            data_schema=self._get_discovery_schema(),
            errors=errors
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual MAC address entry."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS].upper().replace(":", "").replace("-", "")
            # Reformat MAC address
            formatted_mac = ":".join([mac_address[i:i+2] for i in range(0, 12, 2)])
            
            try:
                await self.async_set_unique_id(formatted_mac)
                
                # Check for existing active config entries, not just entity registry
                existing_entries = [
                    entry for entry in self._async_current_entries()
                    if entry.data.get(CONF_MAC_ADDRESS) == formatted_mac
                ]
                
                if existing_entries:
                    errors["base"] = "already_configured"
                elif await self._test_connection(formatted_mac):
                    return self.async_create_entry(
                        title=f"Volcano Hybrid ({formatted_mac})",
                        data={CONF_MAC_ADDRESS: formatted_mac}
                    )
                else:
                    errors["base"] = "cannot_connect"
            except HomeAssistantError:
                errors["base"] = "already_configured"
            except ValueError:
                errors[CONF_MAC_ADDRESS] = "invalid_mac"
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="manual", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors
        )

    def _is_volcano_device(self, discovery_info: BluetoothServiceInfoBleak) -> bool:
        """Check if the discovered device is a Volcano."""
        name = discovery_info.name or ""
        return (
            "volcano" in name.lower() or
            "storz" in name.lower() or
            VOLCANO_SERVICE_UUID.lower() in [uuid.lower() for uuid in discovery_info.service_uuids]
        )

    async def _test_connection(self, mac_address: str) -> bool:
        """Test connection to the device."""
        try:
            api = VolcanoAPI(self.hass, mac_address)
            # Add timeout for connection test
            connected = await asyncio.wait_for(api.connect(), timeout=15.0)
            if connected:
                await api.disconnect()
                return True
        except asyncio.TimeoutError:
            _LOGGER.debug("Connection test timed out for %s", mac_address)
        except Exception as err:
            _LOGGER.debug("Connection test failed: %s", err)
        return False

    async def _scan_for_volcano_devices(self) -> list[dict[str, str]]:
        """Scan for Volcano devices using BleakScanner."""
        try:
            _LOGGER.debug("Scanning for Volcano devices...")
            devices = await BleakScanner.discover(timeout=10.0)
            discovered_devices = []
            
            for device in devices:
                # Check if device.name is not None before looking for "VOLCANO" in it
                if device.name and "VOLCANO" in device.name.upper():
                    discovered_devices.append({
                        "name": device.name,
                        "address": device.address,
                        "display": f"{device.name} - ({device.address})"
                    })
                    _LOGGER.debug("Found VOLCANO device: %s, MAC Address: %s", device.name, device.address)
            
            return discovered_devices
        except Exception as err:
            _LOGGER.error("Error during BLE scan: %s", err)
            return []

    def _get_discovery_schema(self) -> vol.Schema:
        """Get the discovery schema with found devices."""
        if not self._discovered_devices:
            return vol.Schema({})
        
        device_options = {device["display"]: device["display"] for device in self._discovered_devices}
        return vol.Schema({
            vol.Required("device"): vol.In(device_options),
        })

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VolcanoOptionsFlow:
        """Create the options flow."""
        return VolcanoOptionsFlow(config_entry)


class VolcanoOptionsFlow(config_entries.OptionsFlow):
    """Volcano options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("scan_interval", default=30): vol.Coerce(int),
            })
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidMac(HomeAssistantError):
    """Error to indicate invalid MAC address."""
