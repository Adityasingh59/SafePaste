import logging
import threading
import pystray
from PIL import Image, ImageDraw
import customtkinter as ctk
import pyperclip
from typing import Optional

from safepaste.config import Config
from safepaste.pii_detector import PiiDetector
from safepaste.vault import Vault
from safepaste.pseudonymizer import Pseudonymizer
from safepaste.clipboard_monitor import ClipboardMonitor
from safepaste.ui_dashboard import ReviewWindow
from safepaste.ui_settings import SettingsWindow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SafePasteApp:
    def __init__(self):
        self.config = Config()
        self.vault = Vault(ttl_seconds=self.config.vault_ttl)
        self.detector = PiiDetector()
        self.pseudonymizer = Pseudonymizer(self.vault)
        self.monitor = ClipboardMonitor(callback=self.handle_clipboard_change, interval=0.5)
        
        self.icon: Optional[pystray.Icon] = None
        self.root: Optional[ctk.CTk] = None
        
        self.is_paused = False
        
        # Track active windows to prevent duplicates
        self.window_review: Optional[ReviewWindow] = None
        self.window_settings: Optional[SettingsWindow] = None

    def handle_clipboard_change(self, content: str):
        """
        Called by ClipboardMonitor thread when clipboard changes.
        We must schedule UI updates on the main thread.
        """
        if self.root:
            self.root.after(0, self._process_clipboard_content, content)

    def _process_clipboard_content(self, content: str):
        """
        Running on Main Thread.
        Process content, check for re-hydration or PII.
        """
        if self.is_paused:
            return

        # 1. Re-hydration
        if "[" in content and "]" in content:
            # Try re-hydration
            restored = self.pseudonymizer.rehydrate(content)
            if restored != content:
                logger.info("Restored sensitive data from clipboard.")
                self.monitor.update_last_content(restored)
                pyperclip.copy(restored)
                if self.icon:
                    self.icon.notify("Restored original sensitive data.", "SafePaste")
                return

        # 2. Filtering (Length check)
        if len(content) < self.config.min_text_length:
            return

        # 3. PII Detection
        results = self.detector.detect(content)
        if results:
            logger.info(f"Detected {len(results)} PII entities.")
            scrubbed_text = self.pseudonymizer.pseudonymize(content, results)
            
            # Show Review Window
            self.show_review_window(content, scrubbed_text)

    def show_review_window(self, original: str, scrubbed: str):
        if self.window_review and self.window_review.winfo_exists():
            self.window_review.lift()
            return
            
        self.window_review = ReviewWindow(
            original_text=original,
            scrubbed_text=scrubbed,
            on_copy=self.on_copy_clean,
            on_close=lambda: setattr(self, 'window_review', None)
        )

    def on_copy_clean(self, text: str):
        """User clicked 'Copy Clean' in dashboard."""
        logger.info("Copying clean text to clipboard.")
        self.monitor.update_last_content(text)
        try:
            pyperclip.copy(text)
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")

    def create_tray_icon(self):
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color = (0, 128, 0))
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        
        menu = pystray.Menu(
            pystray.MenuItem('Review Dashboard', self.trigger_dashboard_from_tray, enabled=False),
            pystray.MenuItem('Settings', self.trigger_settings_from_tray),
            pystray.MenuItem('Pause Protection', self.toggle_pause, checked=lambda item: self.is_paused),
            pystray.MenuItem('Quit', self.trigger_quit_from_tray)
        )
        
        self.icon = pystray.Icon("SafePaste", image, "SafePaste - Active", menu)
        self.icon.run()

    def trigger_settings_from_tray(self, icon, item):
        if self.root:
            self.root.after(0, self.show_settings_window)

    def trigger_dashboard_from_tray(self, icon, item):
        pass # Only relevant if we store last detection

    def trigger_quit_from_tray(self, icon, item):
        if self.root:
            self.root.after(0, self.quit_app)

    def show_settings_window(self):
        if self.window_settings and self.window_settings.winfo_exists():
            self.window_settings.lift()
            return

        self.window_settings = SettingsWindow(
            config=self.config,
            on_close_callback=lambda: setattr(self, 'window_settings', None)
        )

    def toggle_pause(self, icon, item):
        self.is_paused = not self.is_paused
        # Update icon color? Pystray might need update_menu or icon replacement.
        # Simple for now: just toggle logic.

    def quit_app(self):
        logger.info("Quitting application...")
        self.monitor.stop()
        if self.icon:
            self.icon.stop()
        if self.root:
            self.root.quit()

    def run(self):
        # Initialize Tkinter Root (Hidden)
        self.root = ctk.CTk()
        self.root.withdraw() # Hide the main window
        
        # Start clipboard monitor
        self.monitor.start()
        
        # Start Tray Icon in separate thread
        tray_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        tray_thread.start()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

if __name__ == "__main__":
    app = SafePasteApp()
    app.run()
