"""
main.py

This script provides a system tray application that listens for a hotkey (Ctrl+F9).
When triggered, it converts the current clipboard text from Finglish to Persian using the `f2p` function,
and replaces the clipboard content with the converted text. The application runs a tray icon for quitting.
"""

from pynput import keyboard
import pyperclip
from finglish import f2p
from threading import Thread  # to run tray + hotkey together
from tray import tray
import sys

# Define hotkey combo: Ctrl + F9
COMBO = {keyboard.Key.ctrl_l, keyboard.Key.f9}
current_keys = set()

def on_press(key):
    """
    Handles key press events. If the defined hotkey combination is pressed,
    converts clipboard text from Finglish to Persian and updates the clipboard.
    """
    if key in COMBO:
        current_keys.add(key)

    if COMBO.issubset(current_keys):
        text = pyperclip.paste()

        if text:
            try:
                result = f2p(text)
            except Exception as e:
                # If conversion fails, do nothing
                return
            pyperclip.copy(result)

def on_release(key):
    """
    Handles key release events. Removes released keys from the current_keys set.
    """
    if key in current_keys:
        current_keys.remove(key)

def start_hotkey_listener():
    """
    Starts the keyboard listener in a separate thread to monitor hotkey presses.
    """
    global listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    try:
        listener.join()
    finally:
        listener.stop()  # Ensure cleanup

def on_quit():
    """
    Callback for quitting the application from the tray icon.
    Stops the keyboard listener and exits the program.
    """
    listener.stop()  # Stops the key listener
    sys.exit(0)  # Exit the application

if __name__ == "__main__":
    # Start the hotkey listener in a background thread so the tray icon remains responsive
    Thread(target=start_hotkey_listener, daemon=True).start()

    # Start the PyQt5 tray icon in the main thread; provides a quit option
    tray(on_quit)