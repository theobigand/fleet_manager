import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "fleet.db")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

VEHICLE_STATUSES = {
    "disponible": "Disponible",
    "en_sortie": "En sortie",
    "en_maintenance": "En maintenance",
    "en_panne": "En panne",
    "immobilise": "Immobilisé"
}

VEHICLE_TYPES = ["Voiture", "Utilitaire", "Camionnette", "Camion", "Moto"]

FUEL_TYPES = ["Essence", "Diesel", "Électrique", "Hybride", "GPL"]

SERVICES = ["Direction", "Commercial", "Technique", "Administratif", "Logistique", "RH", "Autre"]

AFFECTATION_TYPES = {
    "mutualise": "Mutualisé (parc partagé)",
    "fonction": "Voiture de fonction"
}

MAINTENANCE_TYPES = [
    "Vidange",
    "Pneus",
    "Freins",
    "Contrôle technique",
    "Réparation",
    "Révision générale",
    "Climatisation",
    "Batterie",
    "Autre"
]

DOCUMENT_TYPES = [
    "Assurance",
    "Contrôle technique",
    "Carte grise",
    "Vignette",
    "Contrat de leasing",
    "Contrat de location"
]

RETURN_STATES = ["Propre", "Sale", "À nettoyer", "Dommages observés"]

FUEL_LEVELS = ["Vide", "1/4", "1/2", "3/4", "Plein"]


COLORS = {
    "disponible": "#90EE90",
    "en_sortie": "#FFB347",
    "en_maintenance": "#FFD700",
    "en_panne": "#FF6B6B",
    "immobilise": "#FF6B6B"
}

DEFAULT_REVISION_KM = 15000
