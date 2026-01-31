from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Sortie:
    id: Optional[int] = None
    vehicule_id: Optional[int] = None
    employe_id: Optional[int] = None
    date_sortie_prevue: Optional[str] = None
    heure_sortie_prevue: Optional[str] = None
    date_retour_prevue: Optional[str] = None
    heure_retour_prevue: Optional[str] = None
    date_sortie_reelle: Optional[str] = None
    heure_sortie_reelle: Optional[str] = None
    km_depart: Optional[int] = None
    date_retour_reelle: Optional[str] = None
    heure_retour_reelle: Optional[str] = None
    km_retour: Optional[int] = None
    motif: Optional[str] = None
    destination: Optional[str] = None
    etat_retour: Optional[str] = None
    niveau_carburant_retour: Optional[str] = None
    statut: str = "en_cours"
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    matricule: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Sortie":
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
    def km_parcourus(self) -> Optional[int]:
        if self.km_retour and self.km_depart:
            return self.km_retour - self.km_depart
        return None
