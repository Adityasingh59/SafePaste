# Pseudonymization functionality
class Pseudonymizer:
    def __init__(self, vault):
        self.vault = vault

    def apply(self, text, spans):
        spans = sorted(spans, key=lambda x: x[0], reverse=True)

        for start, end, label in spans:
            original = text[start:end]
            placeholder = self.vault.get(label, original)
            text = text[:start] + placeholder + text[end:]

        return text