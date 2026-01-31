from typing import Optional, List, Dict, Any
from datetime import date, datetime
from models import Sortie
from dao import SortieDAO, VehicleDAO, UserDAO
from controllers.result import Result


class SortieController:
    
    def __init__(self) -> None:
        self.dao = SortieDAO()
        self.vehicle_dao = VehicleDAO()
        self.log_dao = UserDAO()
    
    def get_en_cours(self) -> List[Sortie]:
        return self.dao.find_en_cours()
    
    def get_historique(self, statut: Optional[str] = None) -> List[Sortie]:
        return self.dao.find_historique(statut)
    
    def get_by_id(self, sortie_id: int) -> Optional[Sortie]:
        return self.dao.find_by_id(sortie_id)
    
    def create_sortie(self, data: Dict[str, Any], user_id: int) -> Result:
        vehicule_id = data.get('vehicule_id')
        employe_id = data.get('employe_id')
        km_depart = data.get('km_depart')
        
        if not vehicule_id:
            return Result.error("Veuillez sélectionner un véhicule")
        if not employe_id:
            return Result.error("Veuillez sélectionner un conducteur")
        if not km_depart or not str(km_depart).isdigit():
            return Result.error("Le kilométrage de départ est obligatoire")
        
        # Vérifier que le véhicule est disponible
        vehicle = self.vehicle_dao.find_by_id(vehicule_id)
        if not vehicle or vehicle.statut != 'disponible':
            return Result.error("Ce véhicule n'est pas disponible")
        
        sortie = Sortie(
            vehicule_id=vehicule_id,
            employe_id=employe_id,
            motif=data.get('motif'),
            destination=data.get('destination'),
            date_sortie_prevue=data.get('date_sortie_prevue'),
            heure_sortie_prevue=data.get('heure_sortie_prevue'),
            date_retour_prevue=data.get('date_retour_prevue'),
            heure_retour_prevue=data.get('heure_retour_prevue'),
            date_sortie_reelle=date.today().isoformat(),
            heure_sortie_reelle=datetime.now().strftime('%H:%M'),
            km_depart=int(km_depart),
            statut='en_cours'
        )
        
        sortie_id = self.dao.create(sortie)
        if sortie_id:
            self.vehicle_dao.update_fields(vehicule_id, statut='en_sortie')
            self.log_dao.add_log(user_id, 'SORTIE_VEHICULE', 
                f"Sortie véhicule {vehicle.immatriculation}")
            return Result.ok(sortie_id, "Sortie enregistrée")
        return Result.error("Erreur lors de la création")
    
    def enregistrer_retour(self, sortie_id: int, data: Dict[str, Any], user_id: int) -> Result:
        sortie = self.dao.find_by_id(sortie_id)
        if not sortie:
            return Result.error("Sortie non trouvée")
        
        km_retour = data.get('km_retour')
        if not km_retour or not str(km_retour).isdigit():
            return Result.error("Le kilométrage de retour est obligatoire")
        
        km_retour = int(km_retour)
        if km_retour < sortie.km_depart:
            return Result.error("Le km de retour ne peut pas être inférieur au km de départ")
        
        nouveau_statut = data.get('nouveau_statut', 'disponible')
        
        # Mise à jour de la sortie
        self.dao.update_fields(sortie_id,
            km_retour=km_retour,
            date_retour_reelle=date.today().isoformat(),
            heure_retour_reelle=datetime.now().strftime('%H:%M'),
            etat_retour=data.get('etat_retour'),
            niveau_carburant_retour=data.get('niveau_carburant'),
            statut='terminee'
        )
        
        # Mise à jour du véhicule
        self.vehicle_dao.update_fields(sortie.vehicule_id,
            statut=nouveau_statut,
            kilometrage_actuel=km_retour
        )
        
        km_parcourus = km_retour - sortie.km_depart
        self.log_dao.add_log(user_id, 'RETOUR_VEHICULE',
            f"Retour {sortie.immatriculation}, {km_parcourus} km")
        
        return Result.ok(message="Retour enregistré")
