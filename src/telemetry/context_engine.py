"""Context engine for processing and analyzing telemetry data"""

from typing import Dict, Any, Optional, List
from collections import deque
import time


class ContextEngine:
    """Processes telemetry data and generates context for AI"""

    def __init__(self, history_size: int = 10):
        """
        Initialize context engine

        Args:
            history_size: Number of telemetry samples to keep in history
        """
        self.history_size = history_size
        self.telemetry_history: deque = deque(maxlen=history_size)
        self.best_lap_time: Optional[float] = None
        self.current_lap_start_time: Optional[float] = None
        self.last_lap_time: Optional[float] = None

    def update(self, telemetry: Dict[str, Any]) -> None:
        """
        Update context with new telemetry data

        Args:
            telemetry: Current telemetry data dictionary
        """
        if not telemetry:
            return

        # Add timestamp if not present
        if "timestamp" not in telemetry:
            telemetry["timestamp"] = time.time()

        # Update best lap time
        if "best_lap_time" in telemetry and telemetry["best_lap_time"]:
            if self.best_lap_time is None or telemetry["best_lap_time"] < self.best_lap_time:
                self.best_lap_time = telemetry["best_lap_time"]

        # Track lap changes
        if "current_lap" in telemetry:
            current_lap = telemetry["current_lap"]
            if hasattr(self, "_last_lap") and current_lap != self._last_lap:
                # New lap started
                self.current_lap_start_time = telemetry.get("timestamp")
            self._last_lap = current_lap

        # Add to history
        self.telemetry_history.append(telemetry.copy())

    def get_context_summary(self) -> str:
        """
        Generate a text summary of current telemetry context

        Returns:
            String summary of current race state
        """
        if not self.telemetry_history:
            return "No telemetry data available."

        current = self.telemetry_history[-1]

        summary_parts = []

        # Speed and gear
        if "speed" in current:
            summary_parts.append(f"Speed: {current['speed']:.1f} km/h")
        if "gear" in current:
            summary_parts.append(f"Gear: {current['gear']}")
        if "rpm" in current:
            summary_parts.append(f"RPM: {current['rpm']}")

        # Lap information
        if "lap_time" in current and current["lap_time"]:
            summary_parts.append(f"Current lap time: {current['lap_time']:.2f}s")
        if self.best_lap_time:
            summary_parts.append(f"Best lap time: {self.best_lap_time:.2f}s")
            if "lap_time" in current and current["lap_time"]:
                delta = current["lap_time"] - self.best_lap_time
                if delta > 0:
                    summary_parts.append(f"Delta: +{delta:.2f}s")
                else:
                    summary_parts.append(f"Delta: {delta:.2f}s")

        # Fuel
        if "fuel" in current:
            summary_parts.append(f"Fuel: {current['fuel']:.1f}L")

        # Tire temperatures
        if "tire_temperatures" in current:
            temps = current["tire_temperatures"]
            avg_temp = sum(temps.values()) / len(temps) if temps else 0
            summary_parts.append(f"Avg tire temp: {avg_temp:.1f}°C")

        # Position
        if "position" in current:
            summary_parts.append(f"Position: P{current['position']}")

        return ". ".join(summary_parts) + "."

    def get_detailed_context(self) -> Dict[str, Any]:
        """
        Get detailed context dictionary for AI processing

        Returns:
            Dictionary with detailed telemetry context
        """
        if not self.telemetry_history:
            return {}

        current = self.telemetry_history[-1]
        context = {
            "current": current,
            "best_lap_time": self.best_lap_time,
            "history_size": len(self.telemetry_history),
        }

        # Calculate deltas if we have history
        if len(self.telemetry_history) > 1:
            previous = self.telemetry_history[-2]
            context["deltas"] = self._calculate_deltas(previous, current)

        # Performance analysis
        context["analysis"] = self._analyze_performance()

        return context

    def _calculate_deltas(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate deltas between two telemetry samples"""
        deltas = {}

        if "speed" in previous and "speed" in current:
            deltas["speed"] = current["speed"] - previous["speed"]

        if "fuel" in previous and "fuel" in current:
            deltas["fuel"] = current["fuel"] - previous["fuel"]

        if "rpm" in previous and "rpm" in current:
            deltas["rpm"] = current["rpm"] - previous["rpm"]

        return deltas

    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance trends"""
        analysis = {}

        if len(self.telemetry_history) < 2:
            return analysis

        # Check tire temperature trends
        if all("tire_temperatures" in t for t in self.telemetry_history[-3:]):
            recent_temps = [
                sum(t["tire_temperatures"].values()) / len(t["tire_temperatures"])
                for t in self.telemetry_history[-3:]
            ]
            if len(recent_temps) >= 2:
                analysis["tire_temp_trend"] = "increasing" if recent_temps[-1] > recent_temps[0] else "decreasing"

        # Check fuel consumption rate
        if all("fuel" in t for t in self.telemetry_history[-5:]):
            fuel_samples = [t["fuel"] for t in self.telemetry_history[-5:]]
            if len(fuel_samples) >= 2:
                fuel_consumption = fuel_samples[0] - fuel_samples[-1]
                analysis["fuel_consumption_rate"] = fuel_consumption

        return analysis

