from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Vehicle:
    id: Optional[int] = None
    immatriculation: str = ""
    marque: str = ""
    modele: str = ""
    type_vehicule: Optional[str] = None
    annee: Optional[int] = None
    date_acquisition: Optional[str] = None
    kilometrage_actuel: int = 0
    carburant: Optional[str] = None
    puissance_fiscale: Optional[int] = None
    numero_chassis: Optional[str] = None
    photo_path: Optional[str] = None
    type_affectation: str = "mutualise"
    statut: str = "disponible"
    service_principal: Optional[str] = None
    seuil_revision_km: int = 15000
    
    @classmethod
    def from_dict(cls, data: dict) -> "Vehicle":
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
    def display_name(self) -> str:
        return f"{self.immatriculation} ({self.marque} {self.modele})"
    
    @property
    def is_available(self) -> bool:
        return self.statut == "disponible"
    
    @property
    def formatted_km(self) -> str:
        return f"{self.kilometrage_actuel:,} km".replace(',', ' ')
