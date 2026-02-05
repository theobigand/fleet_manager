from typing import Optional, List, Dict, Any, Tuple
from models import Vehicle
from dao import VehicleDAO, UserDAO
from controllers.result import Result


class VehicleController:
    
    def __init__(self) -> None:
        self.dao = VehicleDAO()
        self.log_dao = UserDAO()
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Vehicle]:
        return self.dao.find_all(filters)
    
    def get_available(self) -> List[Vehicle]:
        return self.dao.find_available()
    
    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        return self.dao.find_by_id(vehicle_id)
    
    def get_stats(self) -> Dict[str, int]:
        return self.dao.get_stats()
    
    def create(self, data: Dict[str, Any], user_id: int) -> Result:
        # Validation
        immat = data.get('immatriculation', '').strip()
        marque = data.get('marque', '').strip()
        modele = data.get('modele', '').strip()
        
        if not immat:
            return Result.error("L'immatriculation est obligatoire")
        if not marque:
            return Result.error("La marque est obligatoire")
        if not modele:
            return Result.error("Le modèle est obligatoire")
        
        # Vérifier unicité
        if self.dao.find_by_immat(immat.upper()):
            return Result.error("Cette immatriculation existe déjà")
        
        # Créer le véhicule
        vehicle = Vehicle(
            immatriculation=immat.upper(),
            marque=marque,
            modele=modele,
            type_vehicule=data.get('type_vehicule'),
            annee=int(data['annee']) if data.get('annee', '').isdigit() else None,
            date_acquisition=data.get('date_acquisition') or None,
            kilometrage_actuel=int(data.get('kilometrage_actuel', 0)) if str(data.get('kilometrage_actuel', '')).isdigit() else 0,
            carburant=data.get('carburant'),
            puissance_fiscale=int(data['puissance_fiscale']) if data.get('puissance_fiscale', '').isdigit() else None,
            numero_chassis=data.get('numero_chassis'),
            service_principal=data.get('service_principal'),
            type_affectation=data.get('type_affectation', 'mutualise'),
            statut=data.get('statut', 'disponible'),
            seuil_revision_km=int(data.get('seuil_revision_km', 15000)) if str(data.get('seuil_revision_km', '')).isdigit() else 15000,
            photo_path=data.get('photo_path')
        )
        
        vehicle_id = self.dao.create(vehicle)
        if vehicle_id:
            self.log_dao.add_log(user_id, 'CREATION_VEHICULE', f"Création du véhicule {immat}")
            return Result.ok(vehicle_id, "Véhicule créé avec succès")
        return Result.error("Erreur lors de la création")
    
    def update(self, vehicle_id: int, data: Dict[str, Any], user_id: int) -> Result:
        vehicle = self.dao.find_by_id(vehicle_id)
        if not vehicle:
            return Result.error("Véhicule non trouvé")
        
        immat = data.get('immatriculation', '').strip()
        if not immat:
            return Result.error("L'immatriculation est obligatoire")
        
        if immat.upper() != vehicle.immatriculation:
            existing = self.dao.find_by_immat(immat.upper())
            if existing:
                return Result.error("Cette immatriculation existe déjà")
        
        fields = {
            'immatriculation': immat.upper(),
            'marque': data.get('marque', vehicle.marque),
            'modele': data.get('modele', vehicle.modele),
            'type_vehicule': data.get('type_vehicule'),
            'annee': int(data['annee']) if data.get('annee', '') else None,
            'date_acquisition': data.get('date_acquisition') or None,
            'kilometrage_actuel': int(data.get('kilometrage_actuel', 0)) if str(data.get('kilometrage_actuel', '')).isdigit() else vehicle.kilometrage_actuel,
            'carburant': data.get('carburant'),
            'puissance_fiscale': int(data['puissance_fiscale']) if data.get('puissance_fiscale', '') else None,
            'numero_chassis': data.get('numero_chassis'),
            'service_principal': data.get('service_principal'),
            'type_affectation': data.get('type_affectation', 'mutualise'),
            'statut': data.get('statut', vehicle.statut),
            'seuil_revision_km': int(data.get('seuil_revision_km', 15000)) if str(data.get('seuil_revision_km', '')) else vehicle.seuil_revision_km,
            'photo_path': data.get('photo_path')
        }
        
        self.dao.update_fields(vehicle_id, **fields)
        self.log_dao.add_log(user_id, 'MODIFICATION_VEHICULE', f"Modification du véhicule {immat}")
        return Result.ok(message="Véhicule modifié avec succès")
    
    def delete(self, vehicle_id: int, user_id: int) -> Result:
        vehicle = self.dao.find_by_id(vehicle_id)
        if not vehicle:
            return Result.error("Véhicule non trouvé")
    
        conn = self.dao.get_connection()
        try:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM sorties_reservations WHERE vehicule_id = ?", 
                (vehicle_id,)
            )
            count = cursor.fetchone()[0]
        
            if count > 0:
             return Result.error(
                    f"Impossible de supprimer : {count} sortie(s) enregistrée(s) pour ce véhicule.\n"
                    "Supprimez les sorties associées"
                )
        
            cursor = conn.execute(
                "SELECT COUNT(*) FROM affectations_permanentes WHERE vehicule_id = ?", 
                (vehicle_id,)
            )
            affectations = cursor.fetchone()[0]
        
            if affectations > 0:
             return Result.error(
                 "Impossible de supprimer : le véhicule a des affectations permanentes.\n"
                 "Supprimez d'abord les affectations."
             )
        
        finally:
            conn.close()
            self.dao.delete(vehicle_id)
            self.log_dao.add_log(user_id, 'SUPPRESSION_VEHICULE', f"Suppression du véhicule {vehicle.immatriculation}")
            return Result.ok(message="Véhicule supprimé")
    
    def update_status(self, vehicle_id: int, statut: str) -> None:
        self.dao.update_fields(vehicle_id, statut=statut)
    
    def update_km(self, vehicle_id: int, km: int) -> None:
        self.dao.update_fields(vehicle_id, kilometrage_actuel=km)
    
    # Méthodes déléguées au DAO
    def get_affectation(self, vehicle_id: int) -> Dict[str, Any] | None:
        return self.dao.get_affectation(vehicle_id)
    
    def get_sorties(self, vehicle_id: int) -> List[Dict[str, Any]]:
        return self.dao.get_sorties(vehicle_id)
    
    def get_maintenances(self, vehicle_id: int) -> List[Dict[str, Any]]:
        return self.dao.get_maintenances(vehicle_id)
    
    def get_documents(self, vehicle_id: int) -> List[Dict[str, Any]]:
        return self.dao.get_documents(vehicle_id)
    
    def get_ravitaillements(self, vehicle_id: int) -> List[Dict[str, Any]]:
        return self.dao.get_ravitaillements(vehicle_id)
    
    def calculate_consumption(self, vehicle_id: int) -> float | None:
        return self.dao.calculate_consumption(vehicle_id)
