from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Maintenance:
    id: Optional[int] = None
    vehicule_id: Optional[int] = None
    date: Optional[str] = None
    type_intervention: Optional[str] = None
    kilometrage: Optional[int] = None
    cout: Optional[float] = None
    prestataire: Optional[str] = None
    remarques: Optional[str] = None
    date_prochaine_echeance: Optional[str] = None
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Maintenance":
        if not data:
            return None
        filtered_data = {}
        for k, v in data.items():
            if k in cls.__dataclass_fields__:
                filtered_data[k] = v
        return cls(**filtered_data)
    
    def to_dict(self) -> dict:
        return asdict(self)
