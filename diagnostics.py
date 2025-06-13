"""Diagnostics support for Volcano Hybrid."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import VolcanoCoordinator
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: VolcanoCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    return {
        "device_info": {
            "mac_address": coordinator._mac_address,
            "connection_state": coordinator.volcano_api.is_connected,
            "last_update": coordinator.last_update_success_time.isoformat() if coordinator.last_update_success_time else None,
            "update_interval": coordinator.update_interval.total_seconds(),
        },
        "current_state": coordinator.data,
        "config_entry": {
            "title": config_entry.title,
            "data": dict(config_entry.data),
            "options": dict(config_entry.options),
            "state": config_entry.state.value,
        },
    }
