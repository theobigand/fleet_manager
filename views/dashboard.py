import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers import VehicleController
from widgets import StatCard, AlertBanner


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.controller = VehicleController()
        self.setup_dashboard()
        self.refresh()

    def setup_dashboard(self) -> None:
        ctk.CTkLabel(self, text="Tableau de bord", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(pady=20)

        stats_frame = ctk.CTkFrame(self, fg_color='transparent')
        stats_frame.pack(fill='x', padx=20, pady=10)

        self.card_total = StatCard(stats_frame, "Total", "0", '#3498db')
        self.card_total.pack(side='left', padx=10, fill='x', expand=True)

        self.card_dispo = StatCard(stats_frame, "Disponibles", "0", '#2ecc71')
        self.card_dispo.pack(side='left', padx=10, fill='x', expand=True)

        self.card_sortie = StatCard(stats_frame, "En sortie", "0", '#f39c12')
        self.card_sortie.pack(side='left', padx=10, fill='x', expand=True)

        self.card_maint = StatCard(stats_frame, "En maintenance", "0", '#e74c3c')
        self.card_maint.pack(side='left', padx=10, fill='x', expand=True)

        self.alert = AlertBanner(self, "PARC COMPLET - Aucun véhicule disponible")

        ctk.CTkLabel(self, text="Véhicules disponibles", font=ctk.CTkFont(size=16, weight='bold'),
                     text_color='#333333').pack(anchor='w', padx=20, pady=(20, 5))

        tree_frame = ctk.CTkFrame(self, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('immat', 'marque', 'modele', 'type', 'km')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

        self.tree.heading('immat', text='Immatriculation')
        self.tree.heading('marque', text='Marque')
        self.tree.heading('modele', text='Modèle')
        self.tree.heading('type', text='Type')
        self.tree.heading('km', text='Kilométrage')

        self.tree.column('immat', width=120)
        self.tree.column('marque', width=100)
        self.tree.column('modele', width=100)
        self.tree.column('type', width=100)
        self.tree.column('km', width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(fill='x', padx=20, pady=10)

        ctk.CTkButton(btn_frame, text="Actualiser", command=self.refresh,
                      fg_color='#3498db', hover_color='#2980b9', width=120).pack(side='left', padx=5)

        ctk.CTkButton(btn_frame, text="Réserver", command=self.reserve,
                      fg_color='#2ecc71', hover_color='#27ae60', width=120,
                      font=ctk.CTkFont(weight='bold')).pack(side='right', padx=5)

    def refresh(self) -> None:
        stats = self.controller.get_stats()
        self.card_total.set_value(str(stats['total']))
        self.card_dispo.set_value(str(stats['disponible']))
        self.card_sortie.set_value(str(stats['en_sortie']))
        self.card_maint.set_value(str(stats['en_maintenance'] + stats.get('en_panne', 0)))

        if stats['disponible'] == 0 and stats['total'] > 0:
            self.alert.show(after=self.card_maint.master)
        else:
            self.alert.hide()

        vehicles = self.controller.get_available()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for v in vehicles:
            self.tree.insert('', 'end', values=(
                v.immatriculation, v.marque, v.modele,
                v.type_vehicule or '-', f"{v.kilometrage_actuel:,} km"
            ), tags=(str(v.id),))

    def reserve(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule")
            return
        veh_id = int(self.tree.item(selection[0])['tags'][0])
        self.app.navigate_to('reservations', vehicle_id=veh_id)
