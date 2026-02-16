import logging
import re
from typing import List, Dict
from presidio_analyzer import RecognizerResult
from safepaste.vault import Vault

logger = logging.getLogger(__name__)

class Pseudonymizer:
    """
    Handles replacement of PII with placeholders and re-hydration.
    """
    def __init__(self, vault: Vault):
        self.vault = vault
        self._counters: Dict[str, int] = {} # entity_type -> count
        self._current_session_map: Dict[str, str] = {} # original -> placeholder (for consistency within one text)

    def pseudonymize(self, text: str, results: List[RecognizerResult]) -> str:
        """
        Replace detected PII in text with placeholders.
        """
        if not results:
            return text

        # Sort results by start index (ascending) to assign numbers Left-to-Right
        results.sort(key=lambda x: x.start)

        self._counters = {}
        self._current_session_map = {}
        
        # temporary list to store replacements to be made
        # (start, end, placeholder)
        replacements = []

        for result in results:
            entity_type = result.entity_type
            start = result.start
            end = result.end
            original_value = text[start:end]
            
            # Check if we already have a placeholder for this specific value in this session
            if original_value in self._current_session_map:
                placeholder = self._current_session_map[original_value]
            else:
                # Generate new placeholder
                count = self._counters.get(entity_type, 0) + 1
                self._counters[entity_type] = count
                placeholder = f"[{entity_type}_{count}]"
                
                # Store in session map and vault
                self._current_session_map[original_value] = placeholder
                self.vault.add(placeholder, original_value)
            
            replacements.append((start, end, placeholder))
        
        # Apply replacements in reverse order (Right-to-Left) to avoid index shifting
        replacements.sort(key=lambda x: x[0], reverse=True)
        
        new_text = text
        for start, end, placeholder in replacements:
            new_text = new_text[:start] + placeholder + new_text[end:]
            
        logger.info(f"Pseudonymized text. {len(results)} entities replaced.")
        return new_text

    def rehydrate(self, text: str) -> str:
        """
        Restore original values from placeholders.
        """
        # Find all patterns looking like [TYPE_NUM]
        # Regex to find placeholders
        pattern = r"\[([A-Z_]+)_\d+\]"
        
        def replace_match(match):
            placeholder = match.group(0)
            original = self.vault.get(placeholder)
            return original if original else placeholder
            
        return re.sub(pattern, replace_match, text)

# Helper function to get entity type mapping if we want custom names (e.g. PERSON -> PERSON)
# For now we use Presidio entity types directly.
