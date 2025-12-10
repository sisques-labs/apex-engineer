"""Push-to-Talk interface for voice input"""

import threading
from typing import Callable, Optional

import keyboard


class PushToTalk:
    """Manages push-to-talk functionality"""

    def __init__(
        self,
        key: str = "SPACE",
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
    ):
        """
        Initialize push-to-talk handler

        Args:
            key: Keyboard key to use for push-to-talk
            on_press: Callback function when key is pressed
            on_release: Callback function when key is released
        """
        self.key = key.lower()
        self.on_press = on_press
        self.on_release = on_release
        self.is_pressed = False
        self.listening = False

    def start(self) -> None:
        """Start listening for push-to-talk key"""
        if self.listening:
            return

        self.listening = True
        keyboard.on_press_key(self.key, self._on_key_press)
        keyboard.on_release_key(self.key, self._on_key_release)

    def stop(self) -> None:
        """Stop listening for push-to-talk key"""
        self.listening = False
        keyboard.unhook_all()

    def _on_key_press(self, event) -> None:
        """Handle key press event"""
        if event.name.lower() == self.key and not self.is_pressed:
            self.is_pressed = True
            if self.on_press:
                self.on_press()

    def _on_key_release(self, event) -> None:
        """Handle key release event"""
        if event.name.lower() == self.key and self.is_pressed:
            self.is_pressed = False
            if self.on_release:
                self.on_release()

    def is_active(self) -> bool:
        """
        Check if push-to-talk is currently active

        Returns:
            True if key is currently pressed, False otherwise
        """
        return self.is_pressed

