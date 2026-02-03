from typing import Optional, List, Dict, Any
from dao.base_dao import BaseDAO


class AffectationDAO(BaseDAO):

    def find_all_active(self) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT a.*, v.immatriculation, v.marque, v.modele,
                   e.nom, e.prenom, e.matricule
            FROM affectations_permanentes a
            JOIN vehicules v ON a.vehicule_id = v.id
            JOIN employes e ON a.employe_id = e.id
            WHERE a.date_fin IS NULL
            ORDER BY a.date_debut DESC
        """, ())

    def has_active_affectation(self, vehicule_id: int) -> bool:
        result = self._fetch_one(
            "SELECT id FROM affectations_permanentes WHERE vehicule_id = ? AND date_fin IS NULL",
            (vehicule_id,)
        )
        return result is not None

    def create(self, vehicule_id: int, employe_id: int, date_debut: str) -> Optional[int]:
        if self.has_active_affectation(vehicule_id):
            raise ValueError("Ce véhicule a déjà une affectation active")

        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO affectations_permanentes (vehicule_id, employe_id, date_debut, date_fin) VALUES (?, ?, ?, NULL)",
            (vehicule_id, employe_id, date_debut)
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def end_affectation(self, affectation_id: int, date_fin: str) -> None:
        self._update('affectations_permanentes', affectation_id, {'date_fin': date_fin})

    def delete(self, affectation_id: int) -> None:
        self._delete('affectations_permanentes', affectation_id)
