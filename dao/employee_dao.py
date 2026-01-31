from typing import Optional, List, Dict, Any
from dao.base_dao import BaseDAO
from models import Employee

class EmployeeDAO(BaseDAO):
    
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Employee]:
        query="SELECT * FROM employes WHERE 1=1"
        params: List[Any] = []
        
        if filters:
            if filters.get('search'):
                search=f"%{filters['search']}%"
                query+=" AND (matricule LIKE ? OR nom LIKE ? OR prenom LIKE ?)"
                params.extend([search, search, search])
            if filters.get('service'):
                query+=" AND service = ?"
                params.append(filters['service'])
            if filters.get('autorise_only'):
                query+=" AND autorise_conduire = 1"
        
        query+=" ORDER BY nom, prenom"
        rows=self._fetch_all(query, tuple(params))
        return [Employee.from_dict(row) for row in rows]
    
    def find_by_id(self, employee_id: int) -> Optional[Employee]:
        row=self._fetch_one("SELECT * FROM employes WHERE id = ?", (employee_id,))
        return Employee.from_dict(row)
    
    def find_by_matricule(self, matricule: str) -> Optional[Employee]:
        row=self._fetch_one("SELECT * FROM employes WHERE matricule = ?", (matricule,))
        return Employee.from_dict(row)
    
    def find_authorized(self) -> List[Employee]:
        return self.find_all({'autorise_only': True})
    
    def create(self, employee: Employee) -> Optional[int]:
        data=employee.to_dict()
        data.pop('id', None)
        return self._insert('employes', data)
    
    def update(self, employee: Employee) -> None:
        data=employee.to_dict()
        employee_id=data.pop('id')
        self._update('employes', employee_id, data)
    
    def update_fields(self, employee_id: int, **fields) -> None:
        self._update('employes', employee_id, fields)
    
    def delete(self, employee_id: int) -> None:
        self._delete('employes', employee_id)
    
    def get_vehicle_affectation(self, employee_id: int) -> Optional[Dict[str, Any]]:
        return self._fetch_one("""
            SELECT v.* FROM affectations_permanentes a
            JOIN vehicules v ON a.vehicule_id = v.id
            WHERE a.employe_id = ? AND (a.date_fin IS NULL OR a.date_fin >= DATE('now'))
        """, (employee_id,))
    
    def get_sorties(self, employee_id: int) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT s.*, v.immatriculation, v.marque, v.modele
            FROM sorties_reservations s
            JOIN vehicules v ON s.vehicule_id = v.id
            WHERE s.employe_id = ?
            ORDER BY s.date_sortie_reelle DESC
        """, (employee_id,))
