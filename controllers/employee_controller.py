# controllers/employee_controller.py - Logique métier des employés
from typing import Optional, List, Dict, Any
from models import Employee
from dao import EmployeeDAO, UserDAO
from controllers.vehicle_controller import Result


class EmployeeController:
    """Controller pour la logique métier des employés"""
    
    def __init__(self):
        self.dao = EmployeeDAO()
        self.log_dao = UserDAO()
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Employee]:
        return self.dao.find_all(filters)
    
    def get_authorized(self) -> List[Employee]:
        return self.dao.find_authorized()
    
    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        return self.dao.find_by_id(employee_id)
    
    def create(self, data: Dict[str, Any], user_id: int) -> Result:
        matricule = data.get('matricule', '').strip()
        nom = data.get('nom', '').strip()
        prenom = data.get('prenom', '').strip()
        
        if not matricule:
            return Result.error("Le matricule est obligatoire")
        if not nom:
            return Result.error("Le nom est obligatoire")
        if not prenom:
            return Result.error("Le prénom est obligatoire")
        
        if self.dao.find_by_matricule(matricule.upper()):
            return Result.error("Ce matricule existe déjà")
        
        employee = Employee(
            matricule=matricule.upper(),
            nom=nom,
            prenom=prenom,
            service=data.get('service'),
            telephone=data.get('telephone'),
            email=data.get('email'),
            num_permis=data.get('num_permis'),
            date_validite_permis=data.get('date_validite_permis') or None,
            autorise_conduire=1 if data.get('autorise_conduire') else 0,
            photo_path=data.get('photo_path')
        )
        
        employee_id = self.dao.create(employee)
        if employee_id:
            self.log_dao.add_log(user_id, 'CREATION_EMPLOYE', f"Création de l'employé {matricule}")
            return Result.ok(employee_id, "Employé créé avec succès")
        return Result.error("Erreur lors de la création")
    
    def update(self, employee_id: int, data: Dict[str, Any], user_id: int) -> Result:
        employee = self.dao.find_by_id(employee_id)
        if not employee:
            return Result.error("Employé non trouvé")
        
        matricule = data.get('matricule', '').strip()
        if not matricule:
            return Result.error("Le matricule est obligatoire")
        
        if matricule.upper() != employee.matricule:
            if self.dao.find_by_matricule(matricule.upper()):
                return Result.error("Ce matricule existe déjà")
        
        fields = {
            'matricule': matricule.upper(),
            'nom': data.get('nom', employee.nom),
            'prenom': data.get('prenom', employee.prenom),
            'service': data.get('service'),
            'telephone': data.get('telephone'),
            'email': data.get('email'),
            'num_permis': data.get('num_permis'),
            'date_validite_permis': data.get('date_validite_permis') or None,
            'autorise_conduire': 1 if data.get('autorise_conduire') else 0,
            'photo_path': data.get('photo_path')
        }
        
        self.dao.update_fields(employee_id, **fields)
        self.log_dao.add_log(user_id, 'MODIFICATION_EMPLOYE', f"Modification de l'employé {matricule}")
        return Result.ok(message="Employé modifié avec succès")
    
    def delete(self, employee_id: int, user_id: int) -> Result:
        employee = self.dao.find_by_id(employee_id)
        if not employee:
            return Result.error("Employé non trouvé")
        
        self.dao.delete(employee_id)
        self.log_dao.add_log(user_id, 'SUPPRESSION_EMPLOYE', f"Suppression de l'employé {employee.matricule}")
        return Result.ok(message="Employé supprimé")
    
    def get_vehicle(self, employee_id: int):
        return self.dao.get_vehicle_affectation(employee_id)
    
    def get_sorties(self, employee_id: int):
        return self.dao.get_sorties(employee_id)
