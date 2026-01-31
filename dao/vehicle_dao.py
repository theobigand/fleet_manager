# dao/vehicle_dao.py - Accès aux données des véhicules
from typing import Optional, List, Dict, Any
from dao.base_dao import BaseDAO
from models import Vehicle


class VehicleDAO(BaseDAO):
    """DAO pour les véhicules - Requêtes SQL uniquement"""
    
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Vehicle]:
        """Récupère tous les véhicules avec filtres optionnels"""
        query = "SELECT * FROM vehicules WHERE 1=1"
        params: List[Any] = []
        
        if filters:
            if filters.get('search'):
                search = f"%{filters['search']}%"
                query += " AND (immatriculation LIKE ? OR marque LIKE ? OR modele LIKE ?)"
                params.extend([search, search, search])
            if filters.get('statut'):
                query += " AND statut = ?"
                params.append(filters['statut'])
            if filters.get('type_vehicule'):
                query += " AND type_vehicule = ?"
                params.append(filters['type_vehicule'])
            if filters.get('type_affectation'):
                query += " AND type_affectation = ?"
                params.append(filters['type_affectation'])
            if filters.get('service'):
                query += " AND service_principal = ?"
                params.append(filters['service'])
            if filters.get('disponible_only'):
                query += " AND statut = 'disponible'"
        
        query += " ORDER BY immatriculation"
        rows = self._fetch_all(query, tuple(params))
        return [Vehicle.from_dict(row) for row in rows]
    
    def find_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        """Récupère un véhicule par son ID"""
        row = self._fetch_one("SELECT * FROM vehicules WHERE id = ?", (vehicle_id,))
        return Vehicle.from_dict(row)
    
    def find_by_immat(self, immatriculation: str) -> Optional[Vehicle]:
        """Récupère un véhicule par son immatriculation"""
        row = self._fetch_one("SELECT * FROM vehicules WHERE immatriculation = ?", (immatriculation,))
        return Vehicle.from_dict(row)
    
    def find_available(self) -> List[Vehicle]:
        """Récupère les véhicules disponibles"""
        return self.find_all({'disponible_only': True})
    
    def create(self, vehicle: Vehicle) -> Optional[int]:
        """Crée un nouveau véhicule"""
        data = vehicle.to_dict()
        data.pop('id', None)
        return self._insert('vehicules', data)
    
    def update(self, vehicle: Vehicle) -> None:
        """Met à jour un véhicule"""
        data = vehicle.to_dict()
        vehicle_id = data.pop('id')
        self._update('vehicules', vehicle_id, data)
    
    def update_fields(self, vehicle_id: int, **fields) -> None:
        """Met à jour certains champs d'un véhicule"""
        self._update('vehicules', vehicle_id, fields)
    
    def delete(self, vehicle_id: int) -> None:
        """Supprime un véhicule"""
        self._delete('vehicules', vehicle_id)
    
    def get_stats(self) -> Dict[str, int]:
        """Récupère les statistiques du parc"""
        conn = self.get_connection()
        stats = {
            'total': conn.execute("SELECT COUNT(*) FROM vehicules").fetchone()[0],
            'disponible': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut = 'disponible'").fetchone()[0],
            'en_sortie': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut = 'en_sortie'").fetchone()[0],
            'en_maintenance': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut = 'en_maintenance'").fetchone()[0],
            'en_panne': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut IN ('en_panne', 'immobilise')").fetchone()[0],
        }
        conn.close()
        return stats
    
    def get_affectation(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
        """Récupère l'affectation permanente d'un véhicule"""
        return self._fetch_one("""
            SELECT a.*, e.nom, e.prenom, e.matricule 
            FROM affectations_permanentes a
            JOIN employes e ON a.employe_id = e.id
            WHERE a.vehicule_id = ? AND (a.date_fin IS NULL OR a.date_fin >= DATE('now'))
        """, (vehicle_id,))
    
    def get_sorties(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Récupère l'historique des sorties d'un véhicule"""
        return self._fetch_all("""
            SELECT s.*, e.nom, e.prenom, e.matricule
            FROM sorties_reservations s
            JOIN employes e ON s.employe_id = e.id
            WHERE s.vehicule_id = ?
            ORDER BY s.date_sortie_reelle DESC
        """, (vehicle_id,))
    
    def get_maintenances(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Récupère l'historique des maintenances d'un véhicule"""
        return self._fetch_all("""
            SELECT * FROM maintenances 
            WHERE vehicule_id = ? 
            ORDER BY date DESC
        """, (vehicle_id,))
    
    def get_documents(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Récupère les documents d'un véhicule"""
        return self._fetch_all("""
            SELECT * FROM documents 
            WHERE vehicule_id = ? 
            ORDER BY date_echeance
        """, (vehicle_id,))
    
    def get_ravitaillements(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Récupère l'historique des ravitaillements d'un véhicule"""
        return self._fetch_all("""
            SELECT r.*, e.nom, e.prenom
            FROM ravitaillements r
            LEFT JOIN employes e ON r.employe_id = e.id
            WHERE r.vehicule_id = ?
            ORDER BY r.date DESC
        """, (vehicle_id,))
    
    def calculate_consumption(self, vehicle_id: int) -> Optional[float]:
        """Calcule la consommation moyenne d'un véhicule"""
        rows = self._fetch_all("""
            SELECT quantite_litres, kilometrage 
            FROM ravitaillements 
            WHERE vehicule_id = ? AND kilometrage IS NOT NULL
            ORDER BY date
        """, (vehicle_id,))
        
        if len(rows) < 2:
            return None
        
        total_litres = sum(r['quantite_litres'] for r in rows[1:])
        km_diff = rows[-1]['kilometrage'] - rows[0]['kilometrage']
        
        if km_diff <= 0:
            return None
        
        return round((total_litres / km_diff) * 100, 2)
