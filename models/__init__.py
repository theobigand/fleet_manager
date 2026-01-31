# models/__init__.py - Dataclasses pour toutes les entités
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, date


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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @property
    def full_name(self) -> str:
        return f"{self.prenom or ''} {self.nom or ''}".strip() or self.username


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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
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
    # Champs joints (pour les requêtes avec JOIN)
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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @property
    def km_parcourus(self) -> Optional[int]:
        if self.km_retour and self.km_depart:
            return self.km_retour - self.km_depart
        return None


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
    # Champs joints
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Maintenance":
        if not data:
            return None
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)


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
    # Champs joints
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Ravitaillement":
        if not data:
            return None
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Document:
    id: Optional[int] = None
    vehicule_id: Optional[int] = None
    type_document: Optional[str] = None
    date_emission: Optional[str] = None
    date_echeance: Optional[str] = None
    chemin_fichier: Optional[str] = None
    description: Optional[str] = None
    # Champs joints
    immatriculation: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        if not data:
            return None
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
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


@dataclass
class Log:
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: Optional[str] = None
    date_action: Optional[str] = None
    details: Optional[str] = None
    username: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Log":
        if not data:
            return None
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
