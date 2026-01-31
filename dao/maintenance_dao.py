from typing import Optional, List, Dict, Any
from dao.base_dao import BaseDAO
from models import Maintenance, Ravitaillement

class MaintenanceDAO(BaseDAO):
    
    def find_all_maintenances(self, vehicle_immat: Optional[str] = None, type_intervention: Optional[str] = None) -> List[Maintenance]:
        query="""
            SELECT m.*, v.immatriculation, v.marque, v.modele
            FROM maintenances m
            JOIN vehicules v ON m.vehicule_id = v.id
            WHERE 1=1
        """
        params=[]
        if vehicle_immat:
            query+=" AND v.immatriculation = ?"
            params.append(vehicle_immat)
        if type_intervention:
            query+=" AND m.type_intervention = ?"
            params.append(type_intervention)
        query+=" ORDER BY m.date DESC"
        rows = self._fetch_all(query, tuple(params))
        return [Maintenance.from_dict(row) for row in rows]
    
    def find_maintenance_by_id(self, maint_id: int) -> Optional[Maintenance]:
        row=self._fetch_one("SELECT * FROM maintenances WHERE id = ?", (maint_id,))
        return Maintenance.from_dict(row)
    
    def create_maintenance(self, maint: Maintenance) -> Optional[int]:
        data=maint.to_dict()
        data.pop('id', None)
        for key in ['immatriculation', 'marque', 'modele']:
            data.pop(key, None)
        return self._insert('maintenances', data)
    
    def update_maintenance(self, maint_id: int, **fields) -> None:
        self._update('maintenances', maint_id, fields)
    
    def delete_maintenance(self, maint_id: int) -> None:
        self._delete('maintenances', maint_id)
    
    def find_all_ravitaillements(self, vehicle_immat: Optional[str] = None) -> List[Ravitaillement]:
        query="""
            SELECT r.*, v.immatriculation, v.marque, v.modele, e.nom, e.prenom
            FROM ravitaillements r
            JOIN vehicules v ON r.vehicule_id = v.id
            LEFT JOIN employes e ON r.employe_id = e.id
            WHERE 1=1
        """
        params=[]
        if vehicle_immat:
            query+=" AND v.immatriculation = ?"
            params.append(vehicle_immat)
        query+=" ORDER BY r.date DESC"
        rows=self._fetch_all(query, tuple(params))
        return [Ravitaillement.from_dict(row) for row in rows]
    
    def create_ravitaillement(self, rav: Ravitaillement) -> Optional[int]:
        data=rav.to_dict()
        data.pop('id', None)
        for key in ['immatriculation', 'marque', 'modele', 'nom', 'prenom']:
            data.pop(key, None)
        return self._insert('ravitaillements', data)
    
    def delete_ravitaillement(self, rav_id: int) -> None:
        self._delete('ravitaillements', rav_id)
