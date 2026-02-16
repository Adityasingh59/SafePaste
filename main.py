import logging
import threading
import multiprocessing
import ctypes
from ctypes import wintypes
import sys
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

def enforce_single_instance():
    """
    Ensure only one instance of the application is running using a Named Mutex.
    """
    kernel32 = ctypes.windll.kernel32
    mutex_name = "Global\\SafePaste_Instance_Mutex_v1"
    
    # CreateMutexW returns a handle if it exists, but GetLastError will be ERROR_ALREADY_EXISTS
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        logger.error("Another instance of SafePaste is already running.")
        sys.exit(0)
    
    return mutex

class SafePasteApp:
    def __init__(self):
        self.config = Config()
        self.vault = Vault(ttl_seconds=self.config.vault_ttl)
        # Initialize detector lazily or here? 
        # Here is fine, but it takes RAM. 
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
        CRITICAL: Perform Heavy Detection HERE (Background Thread) to avoid freezing Main UI Thread.
        Only schedule UI updates via root.after.
        """
        if self.is_paused:
            return

        try:
            # 1. Re-hydration
            if "[" in content and "]" in content:
                # Try re-hydration
                restored = self.pseudonymizer.rehydrate(content)
                if restored != content:
                    logger.info("Restored sensitive data from clipboard.")
                    self.monitor.update_last_content(restored)
                    
                    # Clipboard write must be careful with threads, but usually fine.
                    # Ideally, do this on main thread if pyperclip has issues, but it usually works.
                    # We will schedule it to be safe and consistent.
                    if self.root:
                        self.root.after(0, self._perform_clipboard_update, restored, "Restored original sensitive data.")
                    return

            # 2. Filtering (Length check)
            if len(content) < self.config.min_text_length:
                return

            # 3. PII Detection (Heavy Operation)
            # This blocks the monitor thread, not the UI thread. Perfect.
            results = self.detector.detect(content)
            
            if results:
                logger.info(f"Detected {len(results)} PII entities.")
                scrubbed_text = self.pseudonymizer.pseudonymize(content, results)
                
                # Show Review Window (Must be on Main Thread)
                if self.root:
                    self.root.after(0, self.show_review_window, content, scrubbed_text)
                    
        except Exception as e:
            logger.error(f"Error in background processing: {e}", exc_info=True)

    def _perform_clipboard_update(self, text: str, notify_msg: Optional[str] = None):
        """Helper to update clipboard from Main Thread."""
        pyperclip.copy(text)
        if notify_msg and self.icon:
            self.icon.notify(notify_msg, "SafePaste")

    def show_review_window(self, original: str, scrubbed: str):
        """Construct and show the review window on the Main Thread."""
        # Check if window already exists
        if self.window_review and self.window_review.winfo_exists():
            # If it exists, maybe update it? Or just bring to front?
            # For now, let's just focus it. 
            self.window_review.lift()
            self.window_review.focus_force()
            return
            
        self.window_review = ReviewWindow(
            original_text=original,
            scrubbed_text=scrubbed,
            on_copy=self.on_copy_clean,
            on_close=lambda: setattr(self, 'window_review', None)
        )
        # Ensure it pops up over other windows
        self.window_review.lift()
        self.window_review.attributes("-topmost", True)
        self.window_review.focus_force()

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
            self.window_settings.focus_force()
            return

        self.window_settings = SettingsWindow(
            config=self.config,
            on_close_callback=lambda: setattr(self, 'window_settings', None)
        )
        self.window_settings.lift()
        self.window_settings.focus_force()

    def toggle_pause(self, icon, item):
        self.is_paused = not self.is_paused
        state = "Paused" if self.is_paused else "Active"
        color = (128, 128, 128) if self.is_paused else (0, 128, 0)
        
        # Update Icon visuals (simple color change)
        img = Image.new('RGB', (64, 64), color=color)
        d = ImageDraw.Draw(img)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        self.icon.icon = img
        self.icon.title = f"SafePaste - {state}"

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
    # CRITICAL: Fix for PyInstaller infinite spawn issue
    multiprocessing.freeze_support()
    
    # CRITICAL: Singleton check
    mutex = enforce_single_instance()
    
    app = SafePasteApp()
    app.run()
