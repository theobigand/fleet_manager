from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, date


@dataclass
class Employee:
    id: Optional[int] = None
    matricule: str = ""
    nom: str = ""
    prenom: str = ""
    service: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    num_permis: Optional[str] = None
    date_validite_permis: Optional[str] = None
    autorise_conduire: int = 0
    photo_path: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
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
        return f"{self.prenom} {self.nom}"
    
    @property
    def is_authorized(self) -> bool:
        return bool(self.autorise_conduire)
    
    @property
    def license_days_left(self) -> Optional[int]:
        if not self.date_validite_permis:
            return None
        try:
            validity = datetime.strptime(self.date_validite_permis, '%Y-%m-%d').date()
            return (validity - date.today()).days
        except ValueError:
            return None
