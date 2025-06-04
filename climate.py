"""Climate platform for Volcano Hybrid."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
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
    """Set up the climate platform."""
    coordinator: VolcanoCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VolcanoClimate(coordinator)])


class VolcanoClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Volcano Hybrid climate device."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1.0
    _attr_min_temp = 40.0
    _attr_max_temp = 230.0

    def __init__(self, coordinator: VolcanoCoordinator) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._mac_address}_climate"
        self._attr_device_info = coordinator.device_info
        self._attr_name = "Volcano Hybrid"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("current_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.coordinator.data.get("target_temperature")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current hvac mode."""
        return HVACMode.HEAT if self.coordinator.data.get("heat_on") else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        try:
            if hvac_mode == HVACMode.HEAT:
                await self.coordinator.volcano_api.set_heat_on()
            elif hvac_mode == HVACMode.OFF:
                await self.coordinator.volcano_api.set_heat_off()
            else:
                _LOGGER.error("Unsupported HVAC mode: %s", hvac_mode)
                return

            await self.coordinator.async_request_refresh()

        except VolcanoConnectionError as err:
            _LOGGER.error("Failed to set HVAC mode: %s", err)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        try:
            await self.coordinator.volcano_api.set_target_temperature(int(temperature))
            await self.coordinator.async_request_refresh()

        except (VolcanoConnectionError, ValueError) as err:
            _LOGGER.error("Failed to set temperature: %s", err)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        super()._handle_coordinator_update()
