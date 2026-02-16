import pytest
from safepaste.pii_detector import PiiDetector

@pytest.fixture(scope="module")
def detector():
    return PiiDetector()

def test_detect_email(detector):
    text = "Contact me at test@example.com for more info."
    results = detector.detect(text)
    assert len(results) >= 1
    assert any(r.entity_type == "EMAIL_ADDRESS" for r in results)

def test_detect_phone(detector):
    text = "Call me at 555-123-4567."
    results = detector.detect(text)
    assert len(results) >= 1
    assert any(r.entity_type == "PHONE_NUMBER" for r in results)

def test_detect_person(detector):
    text = "John Doe is the CEO."
    results = detector.detect(text)
    assert len(results) >= 1
    assert any(r.entity_type == "PERSON" for r in results)

def test_no_pii(detector):
    text = "This is a clean sentence with no private info."
    results = detector.detect(text)
    assert len(results) == 0

def test_empty_string(detector):
    results = detector.detect("")
    assert len(results) == 0
