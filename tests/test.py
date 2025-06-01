"""
Unit tests for main.py: Hotkey-triggered Finglish-to-Persian conversion.

This test suite covers:
- Clipboard integration and conversion logic
- Hotkey detection logic
- Error handling for the f2p conversion
- Integration with the finglish.finglish.f2p function

Requires: pytest, pytest-mock
"""

import pytest
import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Import the functions to test
import main

sys.path.pop(0)

@pytest.fixture(autouse=True)
def reset_clipboard():
    """Automatically reset main._clipboard before each test."""
    if hasattr(main, "_clipboard"):
        delattr(main, "_clipboard")

def load_bulk_f2p_cases():
    test_file = os.path.join(os.path.dirname(__file__), "test.txt")
    with open(test_file, encoding="utf-8") as f:
        return [l.strip().split(' ', 1) for l in f if l.strip()]

def test_f2p_bulk_cases():
    """Bulk test: all cases from finglish/test.txt should pass."""
    from finglish import f2p
    failures = []
    for finglish, expected_persian in load_bulk_f2p_cases():
        persian = f2p(finglish)
        if not persian or persian != expected_persian:
            failures.append(f'For "{finglish}": expected "{expected_persian}", got "{persian}"')
    if failures:
        pytest.fail(f"{len(failures)} failures:\n" + "\n".join(failures))

def test_f2p_conversion(monkeypatch):
    """Test that the f2p conversion is called and clipboard is updated."""
    # Mock clipboard content and f2p result
    test_text = "salam"
    expected_result = "سلام"

    monkeypatch.setattr("pyperclip.paste", lambda: test_text)
    monkeypatch.setattr("pyperclip.copy", lambda x: setattr(main, "_clipboard", x))
    monkeypatch.setattr("finglish.f2p", lambda x: expected_result)

    # Simulate hotkey press
    main.current_keys = set(main.COMBO)
    main.on_press(next(iter(main.COMBO)))  # Call with one key
    # The clipboard should now contain the expected result
    assert getattr(main, "_clipboard", None) == expected_result

def test_f2p_conversion_empty_clipboard(monkeypatch):
    """Test that nothing happens if clipboard is empty."""
    monkeypatch.setattr("pyperclip.paste", lambda: "")
    monkeypatch.setattr("pyperclip.copy", lambda x: setattr(main, "_clipboard", x))
    monkeypatch.setattr("finglish.f2p", lambda x: "should not be called")

    main.current_keys = set(main.COMBO)
    main.on_press(next(iter(main.COMBO)))
    # Clipboard should not be updated
    assert getattr(main, "_clipboard", None) is None

def test_f2p_conversion_exception(monkeypatch):
    """Test that exceptions in f2p are handled gracefully."""
    monkeypatch.setattr("pyperclip.paste", lambda: "test")
    monkeypatch.setattr("pyperclip.copy", lambda x: setattr(main, "_clipboard", x))
    def raise_exc(x): raise Exception("f2p error")
    monkeypatch.setattr("main.f2p", raise_exc)

    main.current_keys = set(main.COMBO)
    main.on_press(next(iter(main.COMBO)))
    # Clipboard should not be updated due to exception
    assert getattr(main, "_clipboard", None) is None

def test_f2p_preserves_spaces_and_punctuation():
    """Test that spaces and punctuation are preserved and converted correctly."""
    from finglish import f2p

    # Single space after comma
    assert f2p("Salam, khoobi?") == "سلام، خوبی؟"
    # Multiple spaces between words
    assert f2p("Salam,   khoobi?") == "سلام،   خوبی؟"
    # Space before punctuation
    assert f2p("Salam , khoobi ?") == "سلام ، خوبی ؟"
    # Leading and trailing spaces
    assert f2p("  Salam, khoobi?  ") == "  سلام، خوبی؟  "
    # Only spaces
    assert f2p("     ") == "     "
    # No spaces
    assert f2p("Salam,khoobi?") == "سلام،خوبی؟"

def test_f2p_handles_only_punctuation():
    """Test that only punctuation is converted correctly."""
    from finglish import f2p

    assert f2p("?") == "؟"
    assert f2p(",") == "،"
    assert f2p(" , ? ") == " ، ؟ "

def test_on_release_removes_key():
    """Test that on_release removes the key from current_keys."""
    main.current_keys = set(main.COMBO)
    key = next(iter(main.COMBO))
    main.on_release(key)
    assert key not in main.current_keys

def test_on_press_adds_key():
    """Test that on_press adds the key to current_keys."""
    main.current_keys = set()
    key = next(iter(main.COMBO))
    main.on_press(key)
    assert key in main.current_keys

@pytest.mark.skip("Integration test: requires GUI event loop and tray, run manually if needed.")
def test_tray_and_listener_integration():
    """Integration test for tray and hotkey listener (manual)."""
    # This test is a placeholder for manual integration testing.
    # You can implement GUI automation or run the app and test manually.
    pass
