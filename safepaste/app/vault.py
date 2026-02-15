# Secure vault storage
import time

TIMEOUT = 60 * 30


class Vault:
    def __init__(self):
        self.map = {}
        self.rev = {}
        self.t = time.time()

    def _cleanup(self):
        if time.time() - self.t > TIMEOUT:
            self.map.clear()
            self.rev.clear()

    def get(self, label, original):
        self._cleanup()
        key = (label, original)

        if key not in self.map:
            count = len([k for k in self.map if k[0] == label]) + 1
            placeholder = f"[{label}_{count}]"
            self.map[key] = placeholder
            self.rev[placeholder] = original

        return self.map[key]

    def rehydrate(self, text):
        self._cleanup()
        for p, o in self.rev.items():
            text = text.replace(p, o)
        return text