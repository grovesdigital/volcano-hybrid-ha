"""Config flow for Volcano Hybrid integration."""
from __future__ import annotations

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

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        
        self._discovered_device = discovery_info
        self._mac_address = discovery_info.address
          # Create entry without testing connection (will be tested during setup)
        return self.async_create_entry(
            title=f"Volcano Hybrid ({discovery_info.address})",
            data={CONF_MAC_ADDRESS: discovery_info.address}
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None, config_entry = None
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
        """Handle device discovery step."""
        if user_input is not None:
            selected_device = user_input["device"]
            mac_address = selected_device.split(" - ")[1].strip("()")
            
            try:
                await self.async_set_unique_id(mac_address)
                self._abort_if_unique_id_configured()
                
                if await self._test_connection(mac_address):
                    return self.async_create_entry(
                        title=f"Volcano Hybrid ({mac_address})",
                        data={CONF_MAC_ADDRESS: mac_address}
                    )
                else:
                    return self.async_show_form(
                        step_id="discovery",
                        data_schema=self._get_discovery_schema(),
                        errors={"base": "cannot_connect"}
                    )
            except Exception as err:
                _LOGGER.exception("Error setting up discovered device: %s", err)
                return self.async_show_form(
                    step_id="discovery",
                    data_schema=self._get_discovery_schema(),
                    errors={"base": "unknown"}
                )

        # Scan for devices
        try:
            discovered_devices = await self._scan_for_volcano_devices()
            if not discovered_devices:
                return self.async_show_form(
                    step_id="discovery",
                    data_schema=vol.Schema({}),
                    errors={"base": "no_devices_found"},
                    description_placeholders={
                        "description": "No Volcano devices found. Make sure your device is turned on and nearby."
                    }
                )
            
            self._discovered_devices = discovered_devices
            return self.async_show_form(
                step_id="discovery",
                data_schema=self._get_discovery_schema(),
                description_placeholders={
                    "description": f"Found {len(discovered_devices)} Volcano device(s). Select one to configure:"
                }
            )
        except Exception as err:
            _LOGGER.exception("Error during device discovery: %s", err)
            return await self.async_step_manual()

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
                self._abort_if_unique_id_configured()
                
                if await self._test_connection(formatted_mac):
                    return self.async_create_entry(
                        title=f"Volcano Hybrid ({formatted_mac})",
                        data={CONF_MAC_ADDRESS: formatted_mac}
                    )
                else:
                    errors["base"] = "cannot_connect"
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

    @staticmethod
    def _is_volcano_device(discovery_info: BluetoothServiceInfoBleak) -> bool:
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
            connected = await api.connect()
            if connected:
                await api.disconnect()
                return True
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
