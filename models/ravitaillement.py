from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Ravitaillement:
    id: Optional[int] = None
    vehicule_id: Optional[int] = None
    employe_id: Optional[int] = None
    date: Optional[str] = None
    quantite_litres: Optional[float] = None
    cout: Optional[float] = None
    station: Optional[str] = None
    kilometrage: Optional[int] = None
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Ravitaillement":
        if not data:
            return None
        filtered_data = {}
        for k, v in data.items():
            if k in cls.__dataclass_fields__:
                filtered_data[k] = v
        return cls(**filtered_data)
    
    def to_dict(self) -> dict:
        return asdict(self)
