"""Button platform for Volcano Hybrid."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TEMP_PRESETS
from . import VolcanoCoordinator
from .volcano.exceptions import VolcanoConnectionError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator: VolcanoCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Temperature preset buttons
    for preset_name, temperature in TEMP_PRESETS.items():
        entities.append(VolcanoPresetButton(coordinator, preset_name, temperature))
    
    # Special action buttons
    entities.extend([
        VolcanoNextSessionButton(coordinator),
        VolcanoQuickSessionButton(coordinator),
    ])
    
    async_add_entities(entities)


class VolcanoPresetButton(CoordinatorEntity, ButtonEntity):
    """Temperature preset button."""

    def __init__(self, coordinator: VolcanoCoordinator, preset_name: str, temperature: int) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._preset_name = preset_name
        self._temperature = temperature
        self._attr_unique_id = f"{coordinator._mac_address}_preset_{preset_name}"
        self._attr_device_info = coordinator.device_info
        self._attr_name = f"Volcano {preset_name.title()} ({temperature}°C)"
        self._attr_icon = "mdi:thermometer"

    async def async_press(self) -> None:
        """Press the button."""
        try:
            await self.coordinator.volcano_api.set_target_temperature(self._temperature)
            await self.coordinator.volcano_api.set_heat_on()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Activated %s preset (%d°C)", self._preset_name, self._temperature)

        except VolcanoConnectionError as err:
            _LOGGER.error("Failed to activate preset %s: %s", self._preset_name, err)


class VolcanoNextSessionButton(CoordinatorEntity, ButtonEntity):
    """Next session button - cycles through temperature presets."""

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_next_session"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Next Session"
        self._attr_icon = "mdi:skip-next"

    async def async_press(self) -> None:
        """Press the button."""
        try:
            await self.coordinator.volcano_api.next_temperature_preset()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Activated next session preset")

        except VolcanoConnectionError as err:
            _LOGGER.error("Failed to activate next session: %s", err)


class VolcanoQuickSessionButton(CoordinatorEntity, ButtonEntity):
    """Quick session button - starts heating at balanced temperature."""

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_quick_session"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Quick Session"
        self._attr_icon = "mdi:play-circle"

    async def async_press(self) -> None:
        """Press the button."""
        try:
            # Start at balanced temperature (190°C)
            await self.coordinator.volcano_api.set_target_temperature(190)
            await self.coordinator.volcano_api.set_heat_on()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Started quick session at 190°C")

        except VolcanoConnectionError as err:
            _LOGGER.error("Failed to start quick session: %s", err)
