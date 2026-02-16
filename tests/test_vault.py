import pytest
import time
from safepaste.vault import Vault

def test_vault_add_get():
    vault = Vault()
    vault.add("[PERSON_1]", "John Doe")
    assert vault.get("[PERSON_1]") == "John Doe"

def test_vault_expiration():
    vault = Vault(ttl_seconds=1)
    vault.add("[PERSON_1]", "John Doe")
    assert vault.get("[PERSON_1]") == "John Doe"
    time.sleep(1.1)
    assert vault.get("[PERSON_1]") is None

def test_vault_clear():
    vault = Vault()
    vault.add("[PERSON_1]", "John Doe")
    vault.clear()
    assert vault.get("[PERSON_1]") is None
