"""Fan platform for Volcano Hybrid."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import VolcanoCoordinator
from .volcano.exceptions import VolcanoConnectionError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fan platform."""
    coordinator: VolcanoCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VolcanoFan(coordinator)])


class VolcanoFan(CoordinatorEntity, FanEntity):
    """Representation of a Volcano Hybrid fan."""

    _attr_supported_features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = 1  # On/Off only

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_fan"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Hybrid Fan"
        self._timer_task: asyncio.Task | None = None

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        return self.coordinator.data.get("fan_on", False)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on."""
        try:
            await self.coordinator.volcano_api.set_fan_on()
            
            # Handle timer if specified
            duration = kwargs.get("duration")
            if duration:
                await self._schedule_fan_off_timer(duration)
            
            await self.coordinator.async_request_refresh()

        except VolcanoConnectionError as err:
            _LOGGER.error("Failed to turn on fan: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        try:
            # Cancel any existing timer
            if self._timer_task and not self._timer_task.done():
                self._timer_task.cancel()
                self._timer_task = None

            await self.coordinator.volcano_api.set_fan_off()
            await self.coordinator.async_request_refresh()

        except VolcanoConnectionError as err:
            _LOGGER.error("Failed to turn off fan: %s", err)

    async def _schedule_fan_off_timer(self, duration: int) -> None:
        """Schedule fan to turn off after duration seconds."""
        # Cancel existing timer
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()

        async def turn_off_after_delay():
            """Turn off fan after delay."""
            try:
                await asyncio.sleep(duration)
                await self.coordinator.volcano_api.set_fan_off()
                await self.coordinator.async_request_refresh()
                _LOGGER.info("Fan turned off after %d second timer", duration)
            except asyncio.CancelledError:
                _LOGGER.debug("Fan timer cancelled")
            except Exception as err:
                _LOGGER.error("Error in fan timer: %s", err)

        self._timer_task = asyncio.create_task(turn_off_after_delay())

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        super()._handle_coordinator_update()
