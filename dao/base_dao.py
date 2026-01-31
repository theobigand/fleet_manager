# dao/base_dao.py - Classe de base pour tous les DAO
import sqlite3
import os
from typing import Optional, List, Dict, Any, Type, TypeVar
from config import DB_PATH

T = TypeVar('T')


class BaseDAO:
    """Classe de base pour l'accès aux données"""
    
    _schema_initialized = False
    
    @staticmethod
    def get_connection() -> sqlite3.Connection:
        """Retourne une connexion à la base de données"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @classmethod
    def init_schema(cls) -> None:
        """Initialise le schéma de la base de données"""
        if cls._schema_initialized:
            return
        
        conn = cls.get_connection()
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'employe',
                nom TEXT,
                prenom TEXT,
                email TEXT,
                actif INTEGER DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS employes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                service TEXT,
                telephone TEXT,
                email TEXT,
                num_permis TEXT,
                date_validite_permis DATE,
                autorise_conduire INTEGER DEFAULT 0,
                photo_path TEXT
            );
            
            CREATE TABLE IF NOT EXISTS vehicules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                immatriculation TEXT UNIQUE NOT NULL,
                marque TEXT NOT NULL,
                modele TEXT NOT NULL,
                type_vehicule TEXT,
                annee INTEGER,
                date_acquisition DATE,
                kilometrage_actuel INTEGER DEFAULT 0,
                carburant TEXT,
                puissance_fiscale INTEGER,
                numero_chassis TEXT,
                photo_path TEXT,
                type_affectation TEXT DEFAULT 'mutualise',
                statut TEXT DEFAULT 'disponible',
                service_principal TEXT,
                seuil_revision_km INTEGER DEFAULT 15000
            );
            
            CREATE TABLE IF NOT EXISTS affectations_permanentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicule_id INTEGER UNIQUE,
                employe_id INTEGER,
                date_debut DATE,
                date_fin DATE,
                FOREIGN KEY (vehicule_id) REFERENCES vehicules(id),
                FOREIGN KEY (employe_id) REFERENCES employes(id)
            );
            
            CREATE TABLE IF NOT EXISTS sorties_reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicule_id INTEGER,
                employe_id INTEGER,
                date_sortie_prevue DATE,
                heure_sortie_prevue TIME,
                date_retour_prevue DATE,
                heure_retour_prevue TIME,
                date_sortie_reelle DATE,
                heure_sortie_reelle TIME,
                km_depart INTEGER,
                date_retour_reelle DATE,
                heure_retour_reelle TIME,
                km_retour INTEGER,
                motif TEXT,
                destination TEXT,
                etat_retour TEXT,
                niveau_carburant_retour TEXT,
                statut TEXT DEFAULT 'en_cours',
                FOREIGN KEY (vehicule_id) REFERENCES vehicules(id),
                FOREIGN KEY (employe_id) REFERENCES employes(id)
            );
            
            CREATE TABLE IF NOT EXISTS maintenances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicule_id INTEGER,
                date DATE,
                type_intervention TEXT,
                kilometrage INTEGER,
                cout REAL,
                prestataire TEXT,
                remarques TEXT,
                date_prochaine_echeance DATE,
                FOREIGN KEY (vehicule_id) REFERENCES vehicules(id)
            );
            
            CREATE TABLE IF NOT EXISTS ravitaillements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicule_id INTEGER,
                employe_id INTEGER,
                date DATE,
                quantite_litres REAL,
                cout REAL,
                station TEXT,
                kilometrage INTEGER,
                FOREIGN KEY (vehicule_id) REFERENCES vehicules(id),
                FOREIGN KEY (employe_id) REFERENCES employes(id)
            );
            
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicule_id INTEGER,
                type_document TEXT,
                date_emission DATE,
                date_echeance DATE,
                chemin_fichier TEXT,
                description TEXT,
                FOREIGN KEY (vehicule_id) REFERENCES vehicules(id)
            );
            
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                date_action DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        conn.commit()
        conn.close()
        cls._schema_initialized = True
    
    def __init__(self):
        self.init_schema()
    
    def _execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Exécute une requête et retourne le curseur"""
        conn = self.get_connection()
        cursor = conn.execute(query, params)
        conn.commit()
        conn.close()
        return cursor
    
    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Exécute une requête et retourne un seul résultat"""
        conn = self.get_connection()
        row = conn.execute(query, params).fetchone()
        conn.close()
        return dict(row) if row else None
    
    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Exécute une requête et retourne tous les résultats"""
        conn = self.get_connection()
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def _insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insère des données et retourne l'ID"""
        # Filtrer les valeurs None pour les champs non obligatoires
        filtered = {k: v for k, v in data.items() if v is not None}
        columns = ", ".join(filtered.keys())
        placeholders = ", ".join("?" * len(filtered))
        
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                list(filtered.values())
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def _update(self, table: str, id: int, data: Dict[str, Any]) -> None:
        """Met à jour des données"""
        if not data:
            return
        sets = ", ".join(f"{k} = ?" for k in data.keys())
        values = list(data.values()) + [id]
        
        conn = self.get_connection()
        conn.execute(f"UPDATE {table} SET {sets} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    def _delete(self, table: str, id: int) -> None:
        """Supprime une entrée"""
        conn = self.get_connection()
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        conn.commit()
        conn.close()
