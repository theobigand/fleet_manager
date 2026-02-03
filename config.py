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
    "mutualise": "Mutualisé",
    "voiture_fonction": "Voiture de fonction",
    "fonction": "Voiture de fonction"  # alias pour compatibilité
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


# Fonctions de formatage pour l'affichage
def format_status(status_key: str) -> str:
    """Convertit une clé de statut en son libellé affichable (ex: 'en_sortie' -> 'En sortie')"""
    return VEHICLE_STATUSES.get(status_key, status_key)


def format_affectation(affectation_key: str) -> str:
    """Convertit une clé d'affectation en son libellé affichable (ex: 'voiture_fonction' -> 'Voiture de fonction')"""
    return AFFECTATION_TYPES.get(affectation_key, affectation_key)


def get_status_key(display_value: str) -> str:
    """Convertit un libellé affichable en sa clé de statut pour la BDD (ex: 'En sortie' -> 'en_sortie')"""
    reverse_map = {v: k for k, v in VEHICLE_STATUSES.items()}
    return reverse_map.get(display_value, display_value)


def get_affectation_key(display_value: str) -> str:
    """Convertit un libellé affichable en sa clé d'affectation pour la BDD"""
    # Préférer 'voiture_fonction' à 'fonction' (alias)
    if display_value == 'Voiture de fonction':
        return 'voiture_fonction'
    if display_value == 'Mutualisé':
        return 'mutualise'
    reverse_map = {v: k for k, v in AFFECTATION_TYPES.items() if k != 'fonction'}
    return reverse_map.get(display_value, display_value)
