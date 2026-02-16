import time
import threading
import logging
import pyperclip

logger = logging.getLogger(__name__)

class ClipboardMonitor:
    """
    Monitors the system clipboard for changes and triggers callbacks.
    """
    def __init__(self, callback, interval: float = 0.5):
        """
        Initialize the ClipboardMonitor.

        Args:
            callback (callable): Function to call when clipboard content changes.
                                 Signature: callback(new_content: str)
            interval (float): Polling interval in seconds (default: 0.5s).
        """
        self.callback = callback
        self.interval = interval
        self.running = False
        self._thread = None
        self._last_content = ""

    def start(self):
        """Start the monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Clipboard monitor started.")

    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self._thread:
            self._thread.join()
        logger.info("Clipboard monitor stopped.")

    def _monitor_loop(self):
        """Internal loop to poll clipboard."""
        # Initialize with current clipboard content to avoid immediate trigger
        try:
            self._last_content = pyperclip.paste()
        except Exception as e:
            logger.error(f"Failed to access clipboard on startup: {e}")
        
        while self.running:
            time.sleep(self.interval)
            try:
                current_content = pyperclip.paste()
                if current_content != self._last_content:
                    self._last_content = current_content
                    # Only trigger if content is text and not empty (optional, but good practice)
                    if isinstance(current_content, str) and current_content.strip():
                        logger.debug("Clipboard change detected.")
                        self.callback(current_content)
            except Exception as e:
                logger.error(f"Error accessing clipboard: {e}")

    def update_last_content(self, content: str):
        """
        Update local cache of clipboard content. 
        Call this when the app programmatically changes the clipboard 
        to prevent self-triggering loops.
        """
        self._last_content = content
