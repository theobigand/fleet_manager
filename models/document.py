from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, date


@dataclass
class Document:
    id: Optional[int] = None
    vehicule_id: Optional[int] = None
    type_document: Optional[str] = None
    date_emission: Optional[str] = None
    date_echeance: Optional[str] = None
    chemin_fichier: Optional[str] = None
    description: Optional[str] = None
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Document":
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
    def days_until_expiry(self) -> Optional[int]:
        if not self.date_echeance:
            return None
        try:
            expiry = datetime.strptime(self.date_echeance, '%Y-%m-%d').date()
            return (expiry - date.today()).days
        except ValueError:
            return None
