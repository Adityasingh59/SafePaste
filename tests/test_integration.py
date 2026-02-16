import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock modules to avoid GUI requirement
sys.modules['customtkinter'] = MagicMock()
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()

from main import SafePasteApp

@patch('main.ClipboardMonitor')
@patch('main.PiiDetector')
@patch('main.Pseudonymizer')
def test_app_initialization(mock_pseudo, mock_detector, mock_monitor):
    app = SafePasteApp()
    assert app.config is not None
    assert app.vault is not None
    assert app.monitor is not None

@patch('main.ClipboardMonitor')
@patch('main.PiiDetector')
@patch('main.Pseudonymizer')
def test_process_clipboard_rehydration(mock_pseudo, mock_detector, mock_monitor):
    app = SafePasteApp()
    
    # Setup mocks
    mock_pseudo_instance = mock_pseudo.return_value
    mock_pseudo_instance.rehydrate.return_value = "John Doe"
    
    # Process content with potential placeholder
    # We must patch root.after since checking checks self.root
    app.root = MagicMock()
    
    # Call _process_clipboard_content directly to test logic
    with patch('pyperclip.copy') as mock_copy:
        app._process_clipboard_content("Hello [PERSON_1]")
        
        mock_pseudo_instance.rehydrate.assert_called_with("Hello [PERSON_1]")
        mock_copy.assert_called_with("John Doe")

@patch('main.ClipboardMonitor')
@patch('main.PiiDetector')
@patch('main.Pseudonymizer')
def test_process_clipboard_pii_detected(mock_pseudo, mock_detector, mock_monitor):
    app = SafePasteApp()
    
    mock_detector_instance = mock_detector.return_value
    mock_detector_instance.detect.return_value = ["fake_result"]
    
    mock_pseudo_instance = mock_pseudo.return_value
    mock_pseudo_instance.pseudonymize.return_value = "Scrubbed"
    
    app.root = MagicMock()
    app.show_review_window = MagicMock()
    
    app._process_clipboard_content("Sensitive Info")
    
    mock_detector_instance.detect.assert_called()
    app.show_review_window.assert_called_with("Sensitive Info", "Scrubbed")
