# Application de Gestion de Parc Automobile d'Entreprise

## Description

Application desktop Python/Tkinter pour la gestion efficace du parc automobile d'une entreprise.

## Fonctionnalités

### Module Gestion des Véhicules
- Ajout/modification/suppression de véhicules
- Recherche multi-critères (immatriculation, marque, modèle, service, statut)
- Filtres par type, statut, affectation
- Affichage avec code couleur (vert: disponible, orange: en sortie, rouge: panne)
- Fiche détaillée avec historique complet
- Alerte "Parc complet" si aucun véhicule disponible

### Module Gestion des Employés
- Gestion des employés autorisés à conduire
- Validation automatique de la date du permis
- Alertes permis proche de l'expiration
- Fiche avec véhicule de fonction et historique des sorties

### Module Tableau de Bord et Réservations
- Résumé du parc (total, disponibles, en sortie, en maintenance)
- Réservation rapide depuis la liste des véhicules disponibles
- Enregistrement des sorties et retours
- Calcul automatique des km parcourus et durée
- Mise à jour automatique des statuts

### Module Maintenance et Carburant
- Enregistrement des interventions de maintenance
- Gestion des ravitaillements carburant
- Calcul automatique de la consommation (L/100km)
- Tableau centralisé des échéances avec alertes visuelles

### Module Documents Administratifs
- Gestion par véhicule: assurance, CT, carte grise, vignette, contrats
- Alertes d'échéance intégrées

### Module Statistiques et Rapports
- Kilométrage par véhicule/période
- Coûts détaillés (carburant, maintenance)
- Taux d'utilisation des véhicules
- Top employés (sorties, km parcourus)
- Graphiques (camemberts, histogrammes) via matplotlib
- Export CSV et PDF

### Module Administration et Sécurité
- Authentification par identifiant/mot de passe
- Mots de passe hachés (SHA256)
- 3 rôles: Administrateur, Gestionnaire, Employé
- Journalisation des actions (logs)

## Installation

### Prérequis
- Python 3.8 ou supérieur
- Tkinter (inclus avec Python sur Windows/Mac, sur Linux: `sudo apt install python3-tk`)

### Installation recommandée (avec venv)
```bash
# 1. Créer l'environnement virtuel
cd fleet_manager
python -m venv venv

# 2. Activer le venv
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py

# 5. Pour désactiver le venv (après utilisation)
deactivate
```

### Installation rapide (sans venv)
```bash
cd fleet_manager
pip install matplotlib reportlab  # Optionnel: pour graphiques et export PDF
python main.py
```

### Note
L'application fonctionne même sans matplotlib et reportlab, mais avec des 
fonctionnalités réduites (pas de graphiques, pas d'export PDF).

## Comptes de test

| Rôle          | Identifiant   | Mot de passe |
|---------------|---------------|--------------|
| Administrateur| admin         | admin123     |
| Gestionnaire  | gestionnaire  | gest123      |
| Employé       | employe       | emp123       |

## Structure du projet

```
fleet_manager/
├── main.py                     # Point d'entrée
├── config.py                   # Configuration et constantes
├── widgets.py                  # Composants UI réutilisables
├── requirements.txt            # Dépendances Python
│
├── controllers/                # Logique métier
│   ├── __init__.py
│   ├── result.py               # Classe Result pour les retours d'opérations
│   ├── auth_controller.py      # Authentification
│   ├── vehicle_controller.py   # Gestion véhicules
│   ├── employee_controller.py  # Gestion employés
│   ├── sortie_controller.py    # Gestion sorties/réservations
│   ├── maintenance_controller.py # Gestion maintenance et ravitaillements
│   ├── document_controller.py  # Gestion documents
│   └── stats_controller.py     # Statistiques et rapports
│
├── dao/                        # Couche d'accès aux données
│   ├── __init__.py
│   ├── base_dao.py             # Classe DAO de base
│   ├── user_dao.py             # Accès données utilisateurs
│   ├── vehicle_dao.py          # Accès données véhicules
│   ├── employee_dao.py         # Accès données employés
│   ├── sortie_dao.py           # Accès données sorties
│   ├── maintenance_dao.py      # Accès données maintenance
│   ├── document_dao.py         # Accès données documents
│   └── stats_dao.py            # Accès données statistiques
│
├── models/                     # Entités métier (dataclasses)
│   ├── __init__.py
│   ├── user.py                 # Modèle User
│   ├── vehicle.py              # Modèle Vehicle
│   ├── employee.py             # Modèle Employee
│   ├── sortie.py               # Modèle Sortie
│   ├── maintenance.py          # Modèle Maintenance
│   ├── ravitaillement.py       # Modèle Ravitaillement
│   ├── document.py             # Modèle Document
│   └── log.py                  # Modèle Log
│
├── views/                      # Interface utilisateur (Tkinter)
│   ├── __init__.py
│   ├── login.py                # Écran de connexion
│   ├── dashboard.py            # Tableau de bord
│   ├── vehicles.py             # Vue gestion véhicules
│   ├── employees.py            # Vue gestion employés
│   ├── reservations.py         # Vue sorties et retours
│   ├── maintenance.py          # Vue maintenance et carburant
│   ├── documents.py            # Vue documents administratifs
│   └── statistics.py           # Vue statistiques et exports
│
├── data/                       # Données persistantes
│   ├── fleet.db                # Base de données SQLite
│   └── create_table.sql        # Script de création des tables
│
└── exports/                    # Fichiers exportés (CSV, PDF)
```

## Architecture

L'application suit une architecture **MVC** (Model-View-Controller) avec une couche **DAO** (Data Access Object) :

- **Models** : Dataclasses représentant les entités métier
- **Views** : Interfaces Tkinter pour l'interaction utilisateur
- **Controllers** : Logique métier et validation
- **DAO** : Abstraction de l'accès à la base de données SQLite

## Base de données

SQLite avec 9 tables:
- `users` - Utilisateurs du système
- `employes` - Employés autorisés à conduire
- `vehicules` - Véhicules du parc
- `affectations_permanentes` - Voitures de fonction
- `sorties_reservations` - Réservations et sorties
- `maintenances` - Interventions de maintenance
- `ravitaillements` - Pleins de carburant
- `documents` - Documents administratifs
- `logs` - Journalisation des actions

## Droits par rôle

| Fonctionnalité              | Admin | Gestionnaire | Employé |
|-----------------------------|-------|--------------|---------|
| Voir tableau de bord        | ✓     | ✓            | ✓       |
| Gérer véhicules             | ✓     | ✓            | ✗       |
| Gérer employés              | ✓     | ✓            | ✗       |
| Réserver/Retourner véhicule | ✓     | ✓            | ✓       |
| Gérer maintenance           | ✓     | ✓            | ✗       |
| Gérer documents             | ✓     | ✓            | ✗       |
| Voir statistiques           | ✓     | ✓            | ✗       |
| Gérer utilisateurs          | ✓     | ✗            | ✗       |
| Voir logs                   | ✓     | ✗            | ✗       |

## Auteur

Roméo AGOSTINO - Mathieu AUDIBERT - Théo BIGAND