import pytest
from presidio_analyzer import RecognizerResult
from safepaste.vault import Vault
from safepaste.pseudonymizer import Pseudonymizer

@pytest.fixture
def pseudonymizer():
    vault = Vault()
    return Pseudonymizer(vault)

def test_pseudonymize_simple(pseudonymizer):
    text = "John Doe"
    results = [RecognizerResult("PERSON", 0, 8, 1.0)]
    anonymized = pseudonymizer.pseudonymize(text, results)
    assert anonymized == "[PERSON_1]"
    assert pseudonymizer.vault.get("[PERSON_1]") == "John Doe"

def test_pseudonymize_consistent(pseudonymizer):
    text = "John Doe met John Doe"
    # Presidio returns distinct results
    results = [
        RecognizerResult("PERSON", 0, 8, 1.0),
        RecognizerResult("PERSON", 13, 21, 1.0)
    ]
    anonymized = pseudonymizer.pseudonymize(text, results)
    assert anonymized == "[PERSON_1] met [PERSON_1]"

def test_pseudonymize_multiple_entities(pseudonymizer):
    text = "John Doe called Jane Smith"
    results = [
        RecognizerResult("PERSON", 0, 8, 1.0),
        RecognizerResult("PERSON", 16, 26, 1.0)
    ]
    anonymized = pseudonymizer.pseudonymize(text, results)
    # Expected: Left-to-Right numbering
    # John Doe -> [PERSON_1]
    # Jane Smith -> [PERSON_2]
    assert anonymized == "[PERSON_1] called [PERSON_2]"
    assert pseudonymizer.vault.get("[PERSON_1]") == "John Doe"
    assert pseudonymizer.vault.get("[PERSON_2]") == "Jane Smith" 

def test_rehydrate(pseudonymizer):
    pseudonymizer.vault.add("[PERSON_1]", "John Doe")
    text = "Hello [PERSON_1]"
    restored = pseudonymizer.rehydrate(text)
    assert restored == "Hello John Doe"
