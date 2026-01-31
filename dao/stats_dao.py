from typing import List, Dict, Any
from dao.base_dao import BaseDAO

class StatsDAO(BaseDAO):
    def get_overview(self) -> Dict[str, Any]:
        conn = self.get_connection()
        stats = {
            'total_vehicles': conn.execute("SELECT COUNT(*) FROM vehicules").fetchone()[0],
            'disponibles': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut = 'disponible'").fetchone()[0],
            'en_sortie': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut = 'en_sortie'").fetchone()[0],
            'en_maintenance': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut = 'en_maintenance'").fetchone()[0],
            'en_panne': conn.execute("SELECT COUNT(*) FROM vehicules WHERE statut IN ('en_panne', 'immobilise')").fetchone()[0],
            'sorties_30j': conn.execute("""
                SELECT COUNT(*) FROM sorties_reservations 
                WHERE date_sortie_reelle >= DATE('now', '-30 days')
            """).fetchone()[0],
            'cout_carburant_30j': conn.execute("""
                SELECT COALESCE(SUM(cout), 0) FROM ravitaillements 
                WHERE date >= DATE('now', '-30 days')
            """).fetchone()[0],
            'cout_maintenance_30j': conn.execute("""
                SELECT COALESCE(SUM(cout), 0) FROM maintenances 
                WHERE date >= DATE('now', '-30 days')
            """).fetchone()[0],
        }
        conn.close()
        return stats
    
    def get_costs_by_vehicle(self) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT v.immatriculation, v.marque, v.modele,
                COALESCE((SELECT SUM(cout) FROM ravitaillements WHERE vehicule_id = v.id), 0) as carburant,
                COALESCE((SELECT SUM(cout) FROM maintenances WHERE vehicule_id = v.id), 0) as maintenance
            FROM vehicules v
            ORDER BY v.immatriculation
        """)
    
    def get_usage_by_vehicle(self) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT v.immatriculation, v.marque, v.modele, v.kilometrage_actuel as km_actuel,
                (SELECT COUNT(*) FROM sorties_reservations 
                 WHERE vehicule_id = v.id AND date_sortie_reelle >= DATE('now', '-30 days')) as sorties_30j,
                (SELECT COUNT(DISTINCT date_sortie_reelle) FROM sorties_reservations 
                 WHERE vehicule_id = v.id AND date_sortie_reelle >= DATE('now', '-30 days')) as jours_utilises,
                ROUND((SELECT COUNT(DISTINCT date_sortie_reelle) FROM sorties_reservations 
                 WHERE vehicule_id = v.id AND date_sortie_reelle >= DATE('now', '-30 days')) * 100.0 / 30, 1) as taux_utilisation
            FROM vehicules v
            ORDER BY sorties_30j DESC
        """)
    
    def get_top_employees(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT e.nom, e.prenom, COUNT(s.id) as nb_sorties,
                COALESCE(SUM(s.km_retour - s.km_depart), 0) as km_total
            FROM employes e
            LEFT JOIN sorties_reservations s ON e.id = s.employe_id AND s.statut = 'terminee'
            GROUP BY e.id
            ORDER BY nb_sorties DESC
            LIMIT ?
        """, (limit,))
    
    def get_monthly_costs(self, months: int = 6) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT strftime('%Y-%m', date) as mois,
                COALESCE(SUM(CASE WHEN type = 'carburant' THEN cout ELSE 0 END), 0) as carburant,
                COALESCE(SUM(CASE WHEN type = 'maintenance' THEN cout ELSE 0 END), 0) as maintenance
            FROM (
                SELECT date, cout, 'carburant' as type FROM ravitaillements
                UNION ALL
                SELECT date, cout, 'maintenance' as type FROM maintenances
            )
            WHERE date >= DATE('now', ? || ' months')
            GROUP BY strftime('%Y-%m', date)
            ORDER BY mois
        """, (f'-{months}',))
    
    def get_all_echeances(self) -> List[Dict[str, Any]]:
        return self._fetch_all("""
            SELECT 'Document' as type, 
                   v.immatriculation || ' - ' || d.type_document as element,
                   d.date_echeance,
                   CAST(julianday(d.date_echeance) - julianday('now') AS INTEGER) as jours_restants
            FROM documents d
            JOIN vehicules v ON d.vehicule_id = v.id
            WHERE d.date_echeance IS NOT NULL
            UNION ALL
            SELECT 'Maintenance' as type,
                   v.immatriculation || ' - ' || m.type_intervention as element,
                   m.date_prochaine_echeance as date_echeance,
                   CAST(julianday(m.date_prochaine_echeance) - julianday('now') AS INTEGER) as jours_restants
            FROM maintenances m
            JOIN vehicules v ON m.vehicule_id = v.id
            WHERE m.date_prochaine_echeance IS NOT NULL
            UNION ALL
            SELECT 'Permis' as type,
                   e.prenom || ' ' || e.nom as element,
                   e.date_validite_permis as date_echeance,
                   CAST(julianday(e.date_validite_permis) - julianday('now') AS INTEGER) as jours_restants
            FROM employes e
            WHERE e.date_validite_permis IS NOT NULL AND e.autorise_conduire = 1
            ORDER BY jours_restants
        """)
