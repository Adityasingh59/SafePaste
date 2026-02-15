import pystray
from PIL import Image
from threading import Thread
from clipboard import start_clipboard_loop


def create_icon():
    return Image.new("RGB", (64, 64), "green")


def run_tray():
    Thread(target=start_clipboard_loop, daemon=True).start()

    icon = pystray.Icon(
        "SafePaste",
        create_icon(),
        menu=pystray.Menu(
            pystray.MenuItem("SafePaste Running", None, enabled=False),
            pystray.MenuItem("Quit", lambda icon, item: icon.stop()),
        ),
    )

    icon.run()