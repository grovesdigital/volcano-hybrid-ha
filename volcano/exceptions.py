"""Custom exceptions for Volcano Hybrid integration."""
from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError


class VolcanoError(HomeAssistantError):
    """Base exception for Volcano Hybrid."""


class VolcanoConnectionError(VolcanoError):
    """Exception for connection errors."""


class VolcanoTimeoutError(VolcanoError):
    """Exception for timeout errors."""


class VolcanoCommandError(VolcanoError):
    """Exception for command execution errors."""
