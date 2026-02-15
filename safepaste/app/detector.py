import re
import spacy
from presidio_analyzer import AnalyzerEngine

EMAIL = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+"
PHONE = r"\\+?\\d[\\d\\-\\(\\) ]{7,}\\d"
API_KEY = r"sk_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
CREDIT = r"\\b(?:\\d[ -]*?){13,16}\\b"


def luhn_valid(num: str) -> bool:
    digits = [int(d) for d in num if d.isdigit()][::-1]
    total = 0
    for i, d in enumerate(digits):
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


class Detector:
    def __init__(self):
        self.presidio = AnalyzerEngine()
        self.nlp = spacy.load("en_core_web_sm")

    def detect(self, text):
        spans = []

        for pattern, label in [
            (EMAIL, "EMAIL"),
            (PHONE, "PHONE"),
            (API_KEY, "API_KEY"),
        ]:
            for m in re.finditer(pattern, text):
                spans.append((m.start(), m.end(), label))

        for m in re.finditer(CREDIT, text):
            if luhn_valid(m.group()):
                spans.append((m.start(), m.end(), "CREDIT_CARD"))

        presidio = self.presidio.analyze(text=text, language="en")
        for p in presidio:
            spans.append((p.start, p.end, p.entity_type))

        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG"]:
                spans.append((ent.start_char, ent.end_char, ent.label_))

        spans = sorted(spans, key=lambda x: x[0])
        filtered = []
        last = -1
        for s in spans:
            if s[0] >= last:
                filtered.append(s)
                last = s[1]

        return filtered