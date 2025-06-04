"""Test configuration for Volcano Hybrid integration."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC_ADDRESS

from custom_components.volcano_hybrid.const import DOMAIN

@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Volcano Hybrid",
        data={CONF_MAC_ADDRESS: "00:11:22:33:44:55"},
        options={},
        source="user",
        entry_id="test_entry_id",
    )

@pytest.fixture
async def mock_volcano_api():
    """Mock Volcano API."""
    class MockVolcanoAPI:
        def __init__(self, hass: HomeAssistant, mac_address: str):
            self.hass = hass
            self.mac_address = mac_address
            self.is_connected = False
            self._device_state = {
                "current_temp": 20,
                "target_temp": 180,
                "heat_on": False,
                "fan_on": False,
                "fan_speed": 0,
            }

        async def connect(self) -> bool:
            """Mock connect."""
            self.is_connected = True
            return True

        async def disconnect(self) -> None:
            """Mock disconnect."""
            self.is_connected = False

        async def get_device_state(self) -> dict:
            """Mock get device state."""
            return self._device_state.copy()

        async def set_temperature(self, temperature: int) -> bool:
            """Mock set temperature."""
            self._device_state["target_temp"] = temperature
            return True

        async def set_heat(self, on: bool) -> bool:
            """Mock set heat."""
            self._device_state["heat_on"] = on
            return True

        async def set_fan(self, on: bool, speed: int = 5) -> bool:
            """Mock set fan."""
            self._device_state["fan_on"] = on
            self._device_state["fan_speed"] = speed if on else 0
            return True

    return MockVolcanoAPI
