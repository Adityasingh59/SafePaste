from dataclasses import dataclass

@dataclass
class Config:
    launch_on_startup: bool = True
    min_text_length: int = 10
    vault_ttl: int = 1800
