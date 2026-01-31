# config.py - Configuration et constantes de l'application
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "fleet.db")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

# Application
APP_TITLE = "Gestion de Parc Automobile d'Entreprise"
APP_VERSION = "1.0.0"

# Statuts véhicule (avec libellés affichage)
VEHICLE_STATUSES = {
    "disponible": "Disponible",
    "en_sortie": "En sortie",
    "en_maintenance": "En maintenance",
    "en_panne": "En panne",
    "immobilise": "Immobilisé"
}

# Types de véhicule
VEHICLE_TYPES = ["Voiture", "Utilitaire", "Camionnette", "Camion", "Moto"]

# Types de carburant
FUEL_TYPES = ["Essence", "Diesel", "Électrique", "Hybride", "GPL"]

# Services/Départements
SERVICES = ["Direction", "Commercial", "Technique", "Administratif", "Logistique", "RH", "Autre"]

# Types d'affectation
AFFECTATION_TYPES = {
    "mutualise": "Mutualisé (parc partagé)",
    "fonction": "Voiture de fonction"
}

# Types de maintenance
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

# Types de documents
DOCUMENT_TYPES = [
    "Assurance",
    "Contrôle technique",
    "Carte grise",
    "Vignette",
    "Contrat de leasing",
    "Contrat de location"
]

# Rôles utilisateur avec niveaux de permission
ROLES = {
    "admin": {"level": 3, "label": "Administrateur"},
    "gestionnaire": {"level": 2, "label": "Gestionnaire de parc"},
    "employe": {"level": 1, "label": "Employé"}
}

# États de retour véhicule
RETURN_STATES = ["Propre", "Sale", "À nettoyer", "Dommages observés"]

# Niveaux de carburant
FUEL_LEVELS = ["Vide", "1/4", "1/2", "3/4", "Plein"]

# Motifs de sortie courants
MOTIFS = [
    "Déplacement professionnel",
    "Rendez-vous client",
    "Livraison",
    "Formation",
    "Réunion externe",
    "Autre"
]

# Couleurs pour les statuts (Treeview)
COLORS = {
    "disponible": "#90EE90",      # Vert clair
    "en_sortie": "#FFB347",       # Orange
    "en_maintenance": "#FFD700",  # Or/Jaune
    "en_panne": "#FF6B6B",        # Rouge clair
    "immobilise": "#FF6B6B"       # Rouge clair
}

# Couleurs pour les alertes échéances
ALERT_COLORS = {
    "expired": "#FF6B6B",         # Rouge - dépassé
    "urgent": "#FFB347",          # Orange - moins de 30 jours
    "ok": "#90EE90"               # Vert - OK
}

# Seuils d'alerte (en jours)
ALERT_THRESHOLD_DAYS = 30

# Seuil par défaut pour révision (en km)
DEFAULT_REVISION_KM = 15000
