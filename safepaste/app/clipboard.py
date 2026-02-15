import time
import pyperclip
from detector import Detector
from pseudonymizer import Pseudonymizer
from vault import Vault
from dashboard import show_dashboard


detector = Detector()
vault = Vault()
pseudo = Pseudonymizer(vault)


def start_clipboard_loop():
    last = ""

    while True:
        try:
            text = pyperclip.paste()

            if text != last and isinstance(text, str) and len(text) > 10:
                last = text

                restored = vault.rehydrate(text)
                if restored != text:
                    pyperclip.copy(restored)
                    continue

                spans = detector.detect(text)

                if spans:
                    clean = pseudo.apply(text, spans)
                    show_dashboard(text, clean)

        except Exception:
            pass

        time.sleep(0.4)