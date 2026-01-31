from typing import Optional, List, Dict, Any
from models import Maintenance, Ravitaillement
from dao import MaintenanceDAO, VehicleDAO, UserDAO
from controllers.result import Result


class MaintenanceController:
    
    def __init__(self) -> None:
        self.dao = MaintenanceDAO()
        self.vehicle_dao = VehicleDAO()
        self.log_dao = UserDAO()
    
    def get_all_maintenances(self, vehicle_immat: Optional[str] = None,
                             type_intervention: Optional[str] = None) -> List[Maintenance]:
        return self.dao.find_all_maintenances(vehicle_immat, type_intervention)
    
    def get_maintenance_by_id(self, maint_id: int) -> Optional[Maintenance]:
        return self.dao.find_maintenance_by_id(maint_id)
    
    def create_maintenance(self, data: Dict[str, Any], user_id: int) -> Result:
        vehicule_id = data.get('vehicule_id')
        date_val = data.get('date')
        type_val = data.get('type_intervention')
        
        if not vehicule_id:
            return Result.error("Véhicule obligatoire")
        if not date_val:
            return Result.error("Date obligatoire")
        if not type_val:
            return Result.error("Type d'intervention obligatoire")
        
        cout_str = data.get('cout', '')
        km_str = data.get('kilometrage', '')
        
        maint = Maintenance(
            vehicule_id=vehicule_id,
            date=date_val,
            type_intervention=type_val,
            kilometrage=int(km_str) if km_str and str(km_str).isdigit() else None,
            cout=float(cout_str) if cout_str and cout_str.replace('.', '').isdigit() else None,
            prestataire=data.get('prestataire'),
            remarques=data.get('remarques'),
            date_prochaine_echeance=data.get('date_prochaine_echeance') or None
        )
        
        maint_id = self.dao.create_maintenance(maint)
        if maint_id:
            self.log_dao.add_log(user_id, 'CREATION_MAINTENANCE', f"{type_val}")
            return Result.ok(maint_id, "Intervention enregistrée")
        return Result.error("Erreur lors de la création")
    
    def update_maintenance(self, maint_id: int, data: Dict[str, Any], user_id: int) -> Result:
        maint = self.dao.find_maintenance_by_id(maint_id)
        if not maint:
            return Result.error("Intervention non trouvée")
        
        cout_str = data.get('cout', '')
        km_str = data.get('kilometrage', '')
        
        fields = {
            'vehicule_id': data.get('vehicule_id', maint.vehicule_id),
            'date': data.get('date', maint.date),
            'type_intervention': data.get('type_intervention', maint.type_intervention),
            'kilometrage': int(km_str) if km_str and str(km_str).isdigit() else None,
            'cout': float(cout_str) if cout_str and cout_str.replace('.', '').isdigit() else None,
            'prestataire': data.get('prestataire'),
            'remarques': data.get('remarques'),
            'date_prochaine_echeance': data.get('date_prochaine_echeance') or None
        }
        
        self.dao.update_maintenance(maint_id, **fields)
        self.log_dao.add_log(user_id, 'MODIFICATION_MAINTENANCE', f"ID {maint_id}")
        return Result.ok(message="Intervention modifiée")
    
    def delete_maintenance(self, maint_id: int, user_id: int) -> Result:
        self.dao.delete_maintenance(maint_id)
        self.log_dao.add_log(user_id, 'SUPPRESSION_MAINTENANCE', f"ID {maint_id}")
        return Result.ok(message="Intervention supprimée")
    
    def get_all_ravitaillements(self, vehicle_immat: Optional[str] = None) -> List[Ravitaillement]:
        return self.dao.find_all_ravitaillements(vehicle_immat)
    
    def create_ravitaillement(self, data: Dict[str, Any], user_id: int) -> Result:
        vehicule_id = data.get('vehicule_id')
        date_val = data.get('date')
        litres = data.get('quantite_litres')
        
        if not vehicule_id:
            return Result.error("Véhicule obligatoire")
        if not date_val:
            return Result.error("Date obligatoire")
        if not litres:
            return Result.error("Quantité obligatoire")
        
        try:
            litres = float(litres)
        except ValueError:
            return Result.error("Quantité invalide")
        
        cout_str = data.get('cout', '')
        km_str = data.get('kilometrage', '')
        
        rav = Ravitaillement(
            vehicule_id=vehicule_id,
            employe_id=data.get('employe_id'),
            date=date_val,
            quantite_litres=litres,
            cout=float(cout_str) if cout_str and cout_str.replace('.', '').isdigit() else None,
            station=data.get('station'),
            kilometrage=int(km_str) if km_str and str(km_str).isdigit() else None
        )
        
        rav_id = self.dao.create_ravitaillement(rav)
        if rav_id:
            self.log_dao.add_log(user_id, 'RAVITAILLEMENT', f"{litres}L")
            return Result.ok(rav_id, "Ravitaillement enregistré")
        return Result.error("Erreur lors de la création")
    
    def delete_ravitaillement(self, rav_id: int, user_id: int) -> Result:
        self.dao.delete_ravitaillement(rav_id)
        self.log_dao.add_log(user_id, 'SUPPRESSION_RAVITAILLEMENT', f"ID {rav_id}")
        return Result.ok(message="Ravitaillement supprimé")
