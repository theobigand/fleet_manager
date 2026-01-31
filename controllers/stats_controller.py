from typing import Dict, Any, List
from datetime import datetime
import os
from dao import StatsDAO, VehicleDAO, UserDAO
from config import EXPORTS_DIR


class StatsController:
    def __init__(self) -> None:
        self.dao = StatsDAO()
        self.vehicle_dao = VehicleDAO()
        self.log_dao = UserDAO()
    
    def get_overview(self) -> Dict[str, Any]:
        return self.dao.get_overview()
    
    def get_costs_by_vehicle(self) -> List[Dict[str, Any]]:
        return self.dao.get_costs_by_vehicle()
    
    def get_usage_by_vehicle(self) -> List[Dict[str, Any]]:
        return self.dao.get_usage_by_vehicle()
    
    def get_top_employees(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.dao.get_top_employees(limit)
    
    def get_monthly_costs(self, months: int = 6) -> List[Dict[str, Any]]:
        return self.dao.get_monthly_costs(months)
    
    def get_all_echeances(self) -> List[Dict[str, Any]]:
        return self.dao.get_all_echeances()
    
    def export_csv(self, user_id: int) -> str:
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        filename = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        stats = self.get_overview()
        costs = self.get_costs_by_vehicle()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("RAPPORT PARC AUTOMOBILE\n")
            f.write(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write("RESUME\n")
            f.write(f"Total véhicules;{stats['total_vehicles']}\n")
            f.write(f"Sorties (30j);{stats['sorties_30j']}\n")
            f.write(f"Coût carburant (30j);{stats['cout_carburant_30j']:.2f}\n")
            f.write(f"Coût maintenance (30j);{stats['cout_maintenance_30j']:.2f}\n\n")
            f.write("COUTS PAR VEHICULE\n")
            f.write("Véhicule;Carburant;Maintenance;Total\n")
            for c in costs:
                t = (c['carburant'] or 0) + (c['maintenance'] or 0)
                f.write(f"{c['immatriculation']};{c['carburant'] or 0:.2f};{c['maintenance'] or 0:.2f};{t:.2f}\n")
        
        self.log_dao.add_log(user_id, 'EXPORT_CSV', filename)
        return filepath
    
    def export_pdf(self, user_id: int) -> str:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
        except ImportError:
            raise ImportError("reportlab non installé")
        
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        filename = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        elements.append(Paragraph("RAPPORT PARC AUTOMOBILE", styles['Title']))
        elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        stats = self.get_overview()
        data = [['Indicateur', 'Valeur'],
                ['Total véhicules', str(stats['total_vehicles'])],
                ['Sorties (30j)', str(stats['sorties_30j'])],
                ['Coût carburant (30j)', f"{stats['cout_carburant_30j']:.2f} €"],
                ['Coût maintenance (30j)', f"{stats['cout_maintenance_30j']:.2f} €"]]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Coûts par véhicule", styles['Heading2']))
        data = [['Véhicule', 'Carburant', 'Maintenance', 'Total']]
        for c in self.get_costs_by_vehicle():
            total = (c['carburant'] or 0) + (c['maintenance'] or 0)
            data.append([c['immatriculation'], f"{c['carburant'] or 0:.2f} €",
                        f"{c['maintenance'] or 0:.2f} €", f"{total:.2f} €"])
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        
        doc.build(elements)
        self.log_dao.add_log(user_id, 'EXPORT_PDF', filename)
        return filepath
