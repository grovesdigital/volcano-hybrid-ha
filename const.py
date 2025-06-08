"""Constants for the Volcano Hybrid integration."""
from __future__ import annotations

from homeassistant.const import Platform
from typing import Final

DOMAIN: Final = "volcano_hybrid"

# Configuration
CONF_MAC_ADDRESS: Final = "mac_address"  # Use this instead of CONF_MAC

# Device constants
DEVICE_NAME: Final = "Volcano Hybrid"
MANUFACTURER: Final = "Storz & Bickel"

# BLE Service UUID for discovery
VOLCANO_SERVICE_UUID: Final = "10100000-5354-4f52-5a26-4249434b454c"

# Update intervals
DEFAULT_SCAN_INTERVAL: Final = 30
FAST_SCAN_INTERVAL: Final = 5

# Platforms
PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.FAN,
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
]

# Temperature constants
MIN_TEMP: Final = 40
MAX_TEMP: Final = 230
DEFAULT_TEMP: Final = 180

# Fan timer constants
MIN_FAN_TIMER: Final = 1
MAX_FAN_TIMER: Final = 300
DEFAULT_FAN_TIMER: Final = 30

# Statistics
STATISTICS_RETENTION_DAYS: Final = 365

# BLE Characteristics UUIDs (from volcanoBleServer.py)
CHAR_HEAT_ON: Final = "1011000f-5354-4f52-5a26-4249434b454c"
CHAR_HEAT_OFF: Final = "10110010-5354-4f52-5a26-4249434b454c"
CHAR_FAN_ON: Final = "10110013-5354-4f52-5a26-4249434b454c"
CHAR_FAN_OFF: Final = "10110014-5354-4f52-5a26-4249434b454c"
CHAR_TARGET_TEMP: Final = "10110003-5354-4f52-5a26-4249434b454c"
CHAR_CURRENT_TEMP: Final = "10110001-5354-4f52-5a26-4249434b454c"
CHAR_STATUS_REGISTER: Final = "1010000c-5354-4f52-5a26-4249434b454c"
CHAR_SCREEN_BRIGHTNESS: Final = "10110005-5354-4f52-5a26-4249434b454c"
CHAR_TARGET_TEMP: Final = "10110003-5354-4f52-5a26-4249434b454c"
CHAR_CURRENT_TEMP: Final = "10110001-5354-4f52-5a26-4249434b454c"
CHAR_STATUS_REGISTER: Final = "1010000c-5354-4f52-5a26-4249434b454c"

# Device information characteristics
CHAR_BLE_FIRMWARE_VERSION: Final = "10100004-5354-4f52-5a26-4249434b454c"
CHAR_SERIAL_NUMBER: Final = "10100008-5354-4f52-5a26-4249434b454c"
CHAR_VOLCANO_FIRMWARE_VERSION: Final = "10100003-5354-4f52-5a26-4249434b454c"
CHAR_BLE_DEVICE: Final = "00000000-0000-0000-0000-000000000420"
CHAR_HOURS_OF_OPERATION: Final = "10110015-5354-4f52-5a26-4249434b454c"  
CHAR_MINUTES_OF_OPERATION: Final = "10110016-5354-4f52-5a26-4249434b454c"

# Temperature presets (Celsius)
TEMP_PRESETS: Final = {
    "flavor": 185,
    "balanced": 190,
    "potent": 195,
    "maximum": 200,
}

# Status register bit masks
STATUS_FAN_ON_MASK: Final = 0x2000
STATUS_HEAT_ON_MASK: Final = 0x0020

# Screen brightness limits
MIN_BRIGHTNESS: Final = 0
MAX_BRIGHTNESS: Final = 100
DEFAULT_BRIGHTNESS: Final = 70

# Services
SERVICE_START_SESSION: Final = "start_session"
SERVICE_TEMPERATURE_SEQUENCE: Final = "temperature_sequence"
