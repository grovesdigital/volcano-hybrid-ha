"""Statistics tracking for Volcano Hybrid usage."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.recorder.statistics import (
    StatisticData,
    StatisticMetaData,
    async_add_external_statistics,
)
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class VolcanoStatistics:
    """Handle usage statistics for Volcano device."""

    def __init__(self, hass: HomeAssistant, device_id: str) -> None:
        """Initialize statistics tracker."""
        self._hass = hass
        self._device_id = device_id
        self._session_start: datetime | None = None
        self._current_session: dict[str, Any] = {}
        self._daily_sessions: list[dict[str, Any]] = []

    async def record_heat_on(self, temperature: float) -> None:
        """Record session start."""
        self._session_start = datetime.now()
        self._current_session = {
            "start_temp": temperature,
            "start_time": self._session_start,
            "temperature_changes": [temperature],
            "peak_temperature": temperature,
        }
        _LOGGER.debug("Session started at %s°C", temperature)

    async def record_temperature_change(self, temperature: float) -> None:
        """Record temperature change during session."""
        if self._current_session:
            self._current_session["temperature_changes"].append(temperature)
            self._current_session["peak_temperature"] = max(
                self._current_session["peak_temperature"], temperature
            )

    async def record_heat_off(self) -> None:
        """Record session end and persist statistics."""
        if not self._session_start:
            return

        duration = datetime.now() - self._session_start
        
        session_data = {
            "duration": duration.total_seconds(),
            "avg_temperature": sum(self._current_session["temperature_changes"]) 
                            / len(self._current_session["temperature_changes"]),
            "max_temperature": self._current_session["peak_temperature"],
            "start_temperature": self._current_session["start_temp"],
            "date": datetime.now().date(),
            "start_time": self._session_start,
            "end_time": datetime.now(),
        }

        # Add to daily sessions
        self._daily_sessions.append(session_data)
        
        # Record in HA statistics
        await self._record_session_statistics(session_data)
        
        # Reset session tracking
        self._session_start = None
        self._current_session = {}
        
        _LOGGER.info(
            "Session completed: %.1f minutes, avg temp %.1f°C", 
            duration.total_seconds() / 60, 
            session_data["avg_temperature"]
        )

    async def _record_session_statistics(self, session_data: dict[str, Any]) -> None:
        """Persist session data to HA statistics."""
        try:
            statistics = [
                StatisticData(
                    start=session_data["start_time"],
                    sum=session_data["duration"],
                    mean=session_data["avg_temperature"],
                    state=session_data["max_temperature"]
                )
            ]

            metadata = StatisticMetaData(
                statistic_id=f"volcano:{self._device_id}:session_duration",
                unit_of_measurement="s",
                has_mean=True,
                has_sum=True,
                name="Volcano Session Duration"
            )

            await async_add_external_statistics(self._hass, metadata, statistics)
            
        except Exception as err:
            _LOGGER.error("Failed to record statistics: %s", err)

    def get_today_sessions(self) -> list[dict[str, Any]]:
        """Get sessions from today."""
        today = datetime.now().date()
        return [s for s in self._daily_sessions if s["date"] == today]

    def get_average_session_duration(self, days: int = 7) -> float:
        """Get average session duration over specified days."""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        recent_sessions = [
            s for s in self._daily_sessions 
            if s["date"] >= cutoff_date
        ]
        
        if not recent_sessions:
            return 0.0
            
        total_duration = sum(s["duration"] for s in recent_sessions)
        return total_duration / len(recent_sessions) / 60  # Return in minutes

    def get_favorite_temperature(self, days: int = 30) -> float | None:
        """Get most frequently used temperature."""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        recent_sessions = [
            s for s in self._daily_sessions 
            if s["date"] >= cutoff_date
        ]
        
        if not recent_sessions:
            return None
            
        # Find most common starting temperature
        temp_counts: dict[float, int] = {}
        for session in recent_sessions:
            temp = session["start_temperature"]
            temp_counts[temp] = temp_counts.get(temp, 0) + 1
            
        return max(temp_counts, key=temp_counts.get) if temp_counts else None

    def get_sessions_today(self) -> int:
        """Get number of sessions today."""
        return len(self.get_today_sessions())

    def get_total_runtime_today(self) -> float:
        """Get total runtime today in minutes."""
        today_sessions = self.get_today_sessions()
        total_seconds = sum(s["duration"] for s in today_sessions)
        return total_seconds / 60

    def get_time_since_last_use(self) -> timedelta | None:
        """Get time since last session ended."""
        if not self._daily_sessions:
            return None
            
        last_session = max(self._daily_sessions, key=lambda s: s["end_time"])
        return datetime.now() - last_session["end_time"]

    async def get_diagnostics(self) -> dict[str, Any]:
        """Get diagnostic information."""
        return {
            "total_sessions": len(self._daily_sessions),
            "sessions_today": self.get_sessions_today(),
            "avg_session_duration_7d": self.get_average_session_duration(7),
            "favorite_temperature_30d": self.get_favorite_temperature(30),
            "total_runtime_today": self.get_total_runtime_today(),
            "time_since_last_use": str(self.get_time_since_last_use()),
            "current_session_active": self._session_start is not None,
        }
