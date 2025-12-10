"""Assetto Corsa shared memory telemetry reader"""

import mmap
import struct
import ctypes
from typing import Dict, Any, Optional
from pathlib import Path
from .telemetry_reader import TelemetryReader


class AssettoCorsaReader(TelemetryReader):
    """Reads telemetry data from Assetto Corsa shared memory"""

    # Shared memory names
    PHYSICS_SHM_NAME = "Local\\acpmf_physics"
    GRAPHICS_SHM_NAME = "Local\\acpmf_graphics"
    STATIC_SHM_NAME = "Local\\acpmf_static"

    def __init__(self):
        """Initialize Assetto Corsa reader"""
        self.physics_shm = None
        self.graphics_shm = None
        self.static_shm = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to Assetto Corsa shared memory

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # On Windows, use named shared memory
            # On Linux/Mac, we'll need a different approach
            import platform

            if platform.system() == "Windows":
                return self._connect_windows()
            else:
                # For Linux/Mac, we might need to use a different method
                # For now, return False and log that Windows is required
                print("Assetto Corsa shared memory currently requires Windows")
                return False
        except Exception as e:
            print(f"Error connecting to Assetto Corsa: {e}")
            return False

    def _connect_windows(self) -> bool:
        """Connect to shared memory on Windows"""
        try:
            import win32file
            import win32con

            # Try to open shared memory objects
            # Note: This is a simplified version - full implementation
            # would need proper struct definitions for AC shared memory
            self.connected = True
            return True
        except ImportError:
            print("pywin32 required for Windows shared memory access")
            return False
        except Exception as e:
            print(f"Error connecting to Windows shared memory: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from shared memory"""
        if self.physics_shm:
            self.physics_shm.close()
            self.physics_shm = None
        if self.graphics_shm:
            self.graphics_shm.close()
            self.graphics_shm = None
        if self.static_shm:
            self.static_shm.close()
            self.static_shm = None
        self.connected = False

    def read(self) -> Optional[Dict[str, Any]]:
        """
        Read current telemetry data from Assetto Corsa

        Returns:
            Dictionary with telemetry data or None if unavailable
        """
        if not self.connected:
            # Return mock data when not connected to real game
            return self._read_mock_data()

        try:
            # TODO: Actual implementation would read from shared memory structures
            # For now, return mock data even when "connected" since full implementation
            # requires proper struct definitions for AC shared memory
            return self._read_mock_data()
        except Exception as e:
            print(f"Error reading telemetry: {e}")
            return None

    def _read_mock_data(self) -> Dict[str, Any]:
        """
        Return mock telemetry data for development/testing
        
        NOTE: These are STATIC test values. In production, this would read
        real-time data from Assetto Corsa shared memory.
        """
        import time
        import random

        # Add slight variations to make it more realistic for testing
        base_speed = 120.5
        base_rpm = 6500
        base_fuel = 45.2
        
        return {
            "speed": base_speed + random.uniform(-5, 5),  # km/h (varies slightly)
            "rpm": int(base_rpm + random.uniform(-200, 200)),
            "gear": 4,
            "fuel": max(0, base_fuel - random.uniform(0, 0.1)),  # Slowly decreasing
            "tire_temperatures": {
                "front_left": 85.0 + random.uniform(-2, 2),
                "front_right": 87.0 + random.uniform(-2, 2),
                "rear_left": 82.0 + random.uniform(-2, 2),
                "rear_right": 84.0 + random.uniform(-2, 2),
            },
            "lap_time": 95.234 + random.uniform(-0.5, 0.5),  # seconds
            "best_lap_time": 94.123,  # Static best time
            "current_lap": 5,
            "position": 3,
            "timestamp": time.time(),
            "_is_mock": True,  # Flag to indicate this is mock data
        }

    def is_connected(self) -> bool:
        """
        Check if connected to Assetto Corsa

        Returns:
            True if connected, False otherwise
        """
        return self.connected

