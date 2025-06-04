"""The Volcano Hybrid integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_MAC_ADDRESS, DOMAIN, PLATFORMS
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
            update_interval=timedelta(seconds=30),
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

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            if not self.volcano_api.is_connected:
                connected = await self.volcano_api.connect()
                if not connected:
                    raise VolcanoConnectionError("Failed to connect to device")

            return await self.volcano_api.get_device_state()
        except VolcanoConnectionError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching data")
            raise UpdateFailed(f"Unexpected error: {err}") from err
