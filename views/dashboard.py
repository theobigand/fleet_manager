import tkinter as tk
from tkinter import ttk, messagebox
from controllers import VehicleController
class DashboardView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='white')
        self.app = app
        self.controller = VehicleController()
        self.setup_dashboard()
        self.refresh()
    
    def setup_dashboard(self):
        tk.Label(self, text="Tableau de bord", font=('Arial', 18, 'bold'), 
                bg='white').pack(pady=20)
        
        # cartes de statistiques
        stats_frame = tk.Frame(self, bg='white')
        stats_frame.pack(fill='x', padx=20, pady=10)
        self.lbl_total = self.create_stat_card(stats_frame, "Total", "0", '#3498db')
        self.lbl_dispo = self.create_stat_card(stats_frame, "Disponibles", "0", '#2ecc71')
        self.lbl_sortie = self.create_stat_card(stats_frame, "En sortie", "0", '#f39c12')
        self.lbl_maint = self.create_stat_card(stats_frame, "En maintenance", "0", '#e74c3c')
        
        # alerte parc complet
        self.alert_frame = tk.Frame(self, bg='#e74c3c', pady=10)
        tk.Label(self.alert_frame, text="⚠️ PARC COMPLET - Aucun véhicule disponible", 
                font=('Arial', 12, 'bold'), bg='#e74c3c').pack()
        
        # titre liste
        tk.Label(self, text="Véhicules disponibles", font=('Arial', 14, 'bold'), 
                bg='white').pack(anchor='w', padx=20, pady=(20, 5))
        
        # treeview
        tree_frame = tk.Frame(self, bg='white')
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
        btn_frame = tk.Frame(self, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(btn_frame, text="Actualiser", command=self.refresh, 
                 bg='#3498db', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Réserver", command=self.reserve, 
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=5)
    
    def create_stat_card(self, parent, title, value, color):
        """Crée une carte de statistique"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.pack(side='left', padx=10, fill='x', expand=True)
        
        tk.Label(card, text=title, font=('Arial', 10), 
                bg=color, fg='white').pack(pady=5)
        
        lbl_value = tk.Label(card, text=value, font=('Arial', 20, 'bold'), 
                            bg=color, fg='white')
        lbl_value.pack(pady=5)
        return lbl_value
    
    def refresh(self):
        """Actualise les données"""

        # stats
        stats = self.controller.get_stats()
        self.lbl_total.config(text=str(stats['total']))
        self.lbl_dispo.config(text=str(stats['disponible']))
        self.lbl_sortie.config(text=str(stats['en_sortie']))
        self.lbl_maint.config(text=str(stats['en_maintenance'] + stats.get('en_panne', 0)))
        
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
            self.tree.insert('', 'end',values=(v.immatriculation, v.marque, v.modele, v.type_vehicule or '-', f"{v.kilometrage_actuel:,} km"))
    
    def reserve(self):
        """Réserver le véhicule sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule")
            return