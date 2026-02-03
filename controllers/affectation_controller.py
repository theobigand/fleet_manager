from typing import List, Dict, Any
from dao import AffectationDAO, VehicleDAO, EmployeeDAO, UserDAO
from controllers.result import Result
from models.employee import Employee
from models.vehicle import Vehicle


class AffectationController:

    def __init__(self) -> None:
        self.dao = AffectationDAO()
        self.vdao = VehicleDAO()
        self.edao = EmployeeDAO()
        self.log_dao = UserDAO()

    def get_all_active(self) -> List[Dict[str, Any]]:
        return self.dao.find_all_active()

    def get_available_vehicles(self) -> List[Vehicle]:
        all_v = self.vdao.find_all()
        active = self.dao.find_all_active()
        affected_ids = {a['vehicule_id'] for a in active}
        return [v for v in all_v if v.id not in affected_ids]

    def get_authorized_employees(self) -> List[Employee]:
        return self.edao.find_authorized()

    def create(self, vehicule_id: int, employe_id: int, date_debut: str, user_id: int) -> Result:
        try:
            self.dao.create(vehicule_id, employe_id, date_debut)
            self.log_dao.add_log(user_id, 'CREATION_AFFECTATION', f'Véhicule {vehicule_id} -> Employé {employe_id}')
            return Result.ok(message="Affectation créée")
        except Exception as e:
            return Result.error(str(e))

    def end(self, affectation_id: int, date_fin: str, user_id: int) -> Result:
        try:
            self.dao.end_affectation(affectation_id, date_fin)
            self.log_dao.add_log(user_id, 'FIN_AFFECTATION', f'Affectation {affectation_id}')
            return Result.ok(message="Affectation terminée")
        except Exception as e:
            return Result.error(str(e))
