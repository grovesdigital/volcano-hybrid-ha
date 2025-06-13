"""Button platform for Volcano Hybrid."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    # Note: Temperature preset buttons and session buttons have been moved to blueprints
    # Users can now create customizable automation blueprints for session management
    # Basic control remains available through climate and fan entities
    
    async_add_entities([])
