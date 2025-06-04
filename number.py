"""Number platform for Volcano Hybrid."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import VolcanoCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator: VolcanoCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        VolcanoFanTimer(coordinator),
        VolcanoScreenBrightness(coordinator),
    ]
    
    async_add_entities(entities)


class VolcanoFanTimer(CoordinatorEntity, NumberEntity):
    """Number entity for fan timer duration."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 5
    _attr_native_max_value = 300
    _attr_native_step = 5
    _attr_native_unit_of_measurement = "s"
    _attr_icon = "mdi:timer"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_fan_timer"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Fan Timer"
        self._timer_value = 36  # Default timer value

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._timer_value

    async def async_set_native_value(self, value: float) -> None:
        """Set the timer value."""
        self._timer_value = int(value)
        _LOGGER.debug("Fan timer set to %d seconds", self._timer_value)

    async def async_start_timer(self) -> None:
        """Start the fan with timer."""
        from .fan import VolcanoFan
        
        # Find the fan entity and start timer
        fan_entities = [
            entity for entity in self.hass.data[DOMAIN].values()
            if isinstance(entity, VolcanoFan)
        ]
        
        if fan_entities:
            fan_entity = fan_entities[0]
            await fan_entity.async_turn_on(duration=self._timer_value)


class VolcanoScreenBrightness(CoordinatorEntity, NumberEntity):
    """Number entity for screen brightness."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 10
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:brightness-6"

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_screen_brightness"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Screen Brightness"
        self._brightness_value = 70  # Default brightness

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._brightness_value

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness value."""
        try:
            brightness = int(value)
            await self.coordinator.volcano_api.set_screen_brightness(brightness)
            self._brightness_value = brightness
            _LOGGER.debug("Screen brightness set to %d%%", brightness)

        except Exception as err:
            _LOGGER.error("Failed to set screen brightness: %s", err)
