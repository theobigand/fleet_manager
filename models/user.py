from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "employe"
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    actif: int = 1
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        if not data:
            return None
        filtered_data = {}
        for k, v in data.items():
            if k in cls.__dataclass_fields__:
                filtered_data[k] = v
        return cls(**filtered_data)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @property
    def full_name(self) -> str:
        return f"{self.prenom or ''} {self.nom or ''}".strip() or self.username
