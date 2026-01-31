from typing import Optional, List, Dict, Any
from dao.base_dao import BaseDAO
from models import Sortie

class SortieDAO(BaseDAO):
    
    def find_by_id(self, sortie_id: int) -> Optional[Sortie]:
        row=self._fetch_one("""
            SELECT s.*, v.immatriculation, v.marque, v.modele, e.nom, e.prenom, e.matricule
            FROM sorties_reservations s
            JOIN vehicules v ON s.vehicule_id = v.id
            JOIN employes e ON s.employe_id = e.id
            WHERE s.id = ?
        """, (sortie_id,))
        return Sortie.from_dict(row)
    
    def find_en_cours(self) -> List[Sortie]:
        rows=self._fetch_all("""
            SELECT s.*, v.immatriculation, v.marque, v.modele, e.nom, e.prenom, e.matricule
            FROM sorties_reservations s
            JOIN vehicules v ON s.vehicule_id = v.id
            JOIN employes e ON s.employe_id = e.id
            WHERE s.statut = 'en_cours'
            ORDER BY s.date_sortie_reelle DESC
        """, ())
        return [Sortie.from_dict(row) for row in rows]
    
    def find_historique(self, statut: Optional[str] = None) -> List[Sortie]:
        query="""
            SELECT s.*, v.immatriculation, v.marque, v.modele, e.nom, e.prenom
            FROM sorties_reservations s
            JOIN vehicules v ON s.vehicule_id = v.id
            JOIN employes e ON s.employe_id = e.id
            WHERE s.statut != 'en_cours'
        """
        params=[]
        if statut:
            query+=" AND s.statut = ?"
            params.append(statut)
        query+=" ORDER BY s.date_retour_reelle DESC"
        rows=self._fetch_all(query, tuple(params))
        return [Sortie.from_dict(row) for row in rows]
    
    def create(self, sortie: Sortie) -> Optional[int]:
        data=sortie.to_dict()
        data.pop('id', None)
        for key in ['immatriculation', 'marque', 'modele', 'nom', 'prenom', 'matricule']:
            data.pop(key, None)
        return self._insert('sorties_reservations', data)
    
    def update_fields(self, sortie_id: int, **fields) -> None:
        self._update('sorties_reservations', sortie_id, fields)
