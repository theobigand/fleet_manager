# views/dashboard.py - Tableau de bord (MVC)
import tkinter as tk
from tkinter import ttk, messagebox

from controllers import VehicleController
from widgets import FilterableTreeview, AlertBanner, StatCard
from config import VEHICLE_STATUSES


class DashboardView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = VehicleController()
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(header, text="Tableau de bord", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')
        tk.Button(header, text="Actualiser", command=self.refresh, bg='#3498db', fg='#000000', relief='flat').pack(side='right')

        cards = tk.Frame(self, bg='#ffffff')
        cards.pack(fill='x', padx=20, pady=10)
        self.card_total = StatCard(cards, "Total véhicules", "0", '#337ab7')
        self.card_total.pack(side='left', padx=10, expand=True, fill='x')
        self.card_dispo = StatCard(cards, "Disponibles", "0", '#5cb85c')
        self.card_dispo.pack(side='left', padx=10, expand=True, fill='x')
        self.card_sortie = StatCard(cards, "En sortie", "0", '#f0ad4e')
        self.card_sortie.pack(side='left', padx=10, expand=True, fill='x')
        self.card_maint = StatCard(cards, "En maintenance", "0", '#d9534f')
        self.card_maint.pack(side='left', padx=10, expand=True, fill='x')

        self.alert_banner = AlertBanner(self, "PARC COMPLET - Aucun véhicule disponible")

        tk.Label(self, text="Véhicules disponibles", font=('Helvetica', 14, 'bold'), bg='#ffffff', fg='#000000').pack(anchor='w', padx=20, pady=(10, 0))

        columns = [('immat', 'Immatriculation', 120), ('marque', 'Marque', 100), ('modele', 'Modèle', 100),
                   ('type', 'Type', 100), ('km', 'Kilométrage', 100), ('service', 'Service', 100)]
        self.tree = FilterableTreeview(self, columns=columns, on_double_click=self._reserve)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        btn = tk.Frame(self, bg='#ffffff')
        btn.pack(fill='x', padx=20, pady=10)
        tk.Button(btn, text="Réserver", command=self._reserve, bg='#27ae60', fg='#000000',
                 font=('Helvetica', 11, 'bold'), relief='flat', pady=8).pack(side='right')
    
    def refresh(self):
        stats = self.controller.get_stats()
        self.card_total.set_value(str(stats['total']))
        self.card_dispo.set_value(str(stats['disponible']))
        self.card_sortie.set_value(str(stats['en_sortie']))
        self.card_maint.set_value(str(stats['en_maintenance'] + stats['en_panne']))
        
        self.alert_banner.show() if stats['disponible'] == 0 and stats['total'] > 0 else self.alert_banner.hide()
        
        vehicles = self.controller.get_available()
        self.tree.clear()
        for v in vehicles:
            self.tree.insert(values=(v.immatriculation, v.marque, v.modele, v.type_vehicule or '-',
                v.formatted_km, v.service_principal or '-'), tags=('disponible', str(v.id)))
    
    def _reserve(self):
        vid = self.tree.get_selected_id(tag_index=1)
        if vid is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule")
            return
        self.app.navigate_to('reservations', preselect_vehicle=vid)
