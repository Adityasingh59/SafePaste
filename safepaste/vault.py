import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class Vault:
    """
    In-memory vault to store mappings between original PII and placeholders.
    Entries expire after a configured duration.
    """
    def __init__(self, ttl_seconds: int = 1800):
        """
        Initialize the Vault.

        Args:
            ttl_seconds (int): Time-to-live for vault entries in seconds (default: 30 mins).
        """
        self.ttl_seconds = ttl_seconds
        self._mapping: Dict[str, str] = {}  # placeholder -> original
        self._timestamps: Dict[str, float] = {} # placeholder -> creation_time

    def add(self, placeholder: str, original: str) -> None:
        """
        Add a mapping to the vault.
        """
        self._mapping[placeholder] = original
        self._timestamps[placeholder] = time.time()
        logger.debug(f"Added to vault: {placeholder}")

    def get(self, placeholder: str) -> Optional[str]:
        """
        Retrieve original value for a placeholder if it hasn't expired.
        """
        if placeholder not in self._mapping:
            return None

        # Check expiration
        if time.time() - self._timestamps[placeholder] > self.ttl_seconds:
            self._remove(placeholder)
            return None

        return self._mapping[placeholder]

    def _remove(self, placeholder: str) -> None:
        """Remove an item from the vault."""
        if placeholder in self._mapping:
            del self._mapping[placeholder]
        if placeholder in self._timestamps:
            del self._timestamps[placeholder]
        logger.debug(f"Removed from vault: {placeholder}")

    def clear(self) -> None:
        """Clear all entries from the vault."""
        self._mapping.clear()
        self._timestamps.clear()
        logger.info("Vault cleared.")

    def cleanup(self) -> None:
        """Remove all expired entries."""
        now = time.time()
        expired = [p for p, t in self._timestamps.items() if now - t > self.ttl_seconds]
        for p in expired:
            self._remove(p)
