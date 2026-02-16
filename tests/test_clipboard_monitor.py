import pytest
import time
from unittest.mock import MagicMock, patch
from safepaste.clipboard_monitor import ClipboardMonitor

@patch("pyperclip.paste")
def test_monitor_callback(mock_paste):
    mock_callback = MagicMock()
    monitor = ClipboardMonitor(callback=mock_callback, interval=0.1)
    
    # Simulate sequence of clipboard contents
    # 1. Initial content "A"
    # 2. Change to "B" -> Trigger
    # 3. Stay "B" -> No Trigger
    # 4. Change to "C" -> Trigger
    mock_paste.side_effect = ["A", "B", "B", "C", "C"]
    
    monitor.start()
    time.sleep(0.4) # Wait for a few loops
    monitor.stop()
    
    assert mock_callback.call_count >= 2
    mock_callback.assert_any_call("B")
    mock_callback.assert_any_call("C")

@patch("pyperclip.paste")
def test_update_last_content(mock_paste):
    mock_callback = MagicMock()
    monitor = ClipboardMonitor(callback=mock_callback, interval=0.1)
    
    # Initial: "A"
    mock_paste.side_effect = ["A", "B", "B"]
    
    monitor.start()
    
    # We programmatically update last content to "B" BEFORE the loop catches it
    monitor.update_last_content("B")
    
    time.sleep(0.3)
    monitor.stop()
    
    # Should NOT trigger callback because we updated last_content manually
    mock_callback.assert_not_called()
