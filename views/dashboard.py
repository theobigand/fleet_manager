import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers import VehicleController


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

        # cartes de statistiques
        stats_frame = ctk.CTkFrame(self, fg_color='transparent')
        stats_frame.pack(fill='x', padx=20, pady=10)

        self.lbl_total = self.create_stat_card(stats_frame, "Total", "0", '#3498db')
        self.lbl_dispo = self.create_stat_card(stats_frame, "Disponibles", "0", '#2ecc71')
        self.lbl_sortie = self.create_stat_card(stats_frame, "En sortie", "0", '#f39c12')
        self.lbl_maint = self.create_stat_card(stats_frame, "En maintenance", "0", '#e74c3c')

        # alerte parc complet
        self.alert_frame = ctk.CTkFrame(self, fg_color='#e74c3c')
        ctk.CTkLabel(self.alert_frame, text="PARC COMPLET - Aucun véhicule disponible",
                     font=ctk.CTkFont(size=14, weight='bold'), text_color='white').pack(pady=10)

        # titre liste
        ctk.CTkLabel(self, text="Véhicules disponibles", font=ctk.CTkFont(size=16, weight='bold'),
                     text_color='#333333').pack(anchor='w', padx=20, pady=(20, 5))

        # treeview
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

        # boutons
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(fill='x', padx=20, pady=10)

        ctk.CTkButton(btn_frame, text="Actualiser", command=self.refresh,
                      fg_color='#3498db', hover_color='#2980b9', width=120).pack(side='left', padx=5)

        ctk.CTkButton(btn_frame, text="Réserver", command=self.reserve,
                      fg_color='#2ecc71', hover_color='#27ae60', width=120,
                      font=ctk.CTkFont(weight='bold')).pack(side='right', padx=5)

    def create_stat_card(self, parent, title, value, color) -> ctk.CTkLabel:
        """Crée une carte de statistique"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.pack(side='left', padx=10, fill='x', expand=True)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12),
                     text_color='white').pack(pady=(10, 5))

        lbl_value = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight='bold'),
                                  text_color='white')
        lbl_value.pack(pady=(5, 10))
        return lbl_value

    def refresh(self) -> None:
        """Actualise les données"""
        # stats
        stats = self.controller.get_stats()
        self.lbl_total.configure(text=str(stats['total']))
        self.lbl_dispo.configure(text=str(stats['disponible']))
        self.lbl_sortie.configure(text=str(stats['en_sortie']))
        self.lbl_maint.configure(text=str(stats['en_maintenance'] + stats.get('en_panne', 0)))

        # alerte parc complet
        if stats['disponible'] == 0 and stats['total'] > 0:
            self.alert_frame.pack(fill='x', padx=20, pady=10, after=self.lbl_maint.master)
        else:
            self.alert_frame.pack_forget()

        # liste véhicules disponibles
        vehicles = self.controller.get_available()

        # vider le treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # remplir avec les véhicules disponibles
        for v in vehicles:
            self.tree.insert('', 'end', values=(
                v.immatriculation, v.marque, v.modele,
                v.type_vehicule or '-', f"{v.kilometrage_actuel:,} km"
            ))

    def reserve(self) -> None:
        """Réserver le véhicule sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule")
            return