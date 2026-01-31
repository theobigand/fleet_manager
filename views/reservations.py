import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from controllers import SortieController, VehicleController, EmployeeController


class ReservationsView(tk.Frame):
    def __init__(self, parent, app, vehicle_id=None):
        super().__init__(parent, bg='white')
        self.app = app
        self.sortie_ctrl = SortieController()
        self.veh_ctrl = VehicleController()
        self.emp_ctrl = EmployeeController()
        self.preselect_veh = vehicle_id
        self.setup_reservation()
        self.refresh()
        
        if vehicle_id:
            self.after(100, lambda: self.new_sortie(vehicle_id))

    def setup_reservation(self):
        # titre
        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=20, pady=20)
        tk.Label(top, text="Réservations & Sorties", font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        tk.Button(top, text="+ Nouvelle sortie", command=lambda: self.new_sortie(), bg='green', fg='white').pack(side='right')

        # onglets
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_tab_en_cours()
        self.create_tab_historique()
    
    def create_tab_en_cours(self):
        tab = tk.Frame(self.tabs, bg='white')
        self.tabs.add(tab, text='En cours')
        
        tk.Label(tab, text="Double-clic pour enregistrer le retour", font=('Arial', 9, 'italic'), 
                bg='white', fg='gray').pack(anchor='w', padx=10, pady=5)
        
        # liste
        cols = ('vehicule', 'conducteur', 'date', 'destination', 'motif', 'km')
        self.tree_cours = ttk.Treeview(tab, columns=cols, show='headings', height=12)
        self.tree_cours.heading('vehicule', text='Véhicule')
        self.tree_cours.heading('conducteur', text='Conducteur')
        self.tree_cours.heading('date', text='Date sortie')
        self.tree_cours.heading('destination', text='Destination')
        self.tree_cours.heading('motif', text='Motif')
        self.tree_cours.heading('km', text='Km départ')
        self.tree_cours.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree_cours.bind('<Double-1>', lambda e: self.retour())
    
    def create_tab_historique(self):
        tab = tk.Frame(self.tabs, bg='white')
        self.tabs.add(tab, text='Historique')
        
        # filtre
        flt = tk.Frame(tab, bg='white')
        flt.pack(fill='x', padx=10, pady=10)
        tk.Label(flt, text="Statut:", bg='white').pack(side='left')
        self.filter = ttk.Combobox(flt, values=['Tous', 'terminee', 'annulee'], width=12)
        self.filter.set('Tous')
        self.filter.pack(side='left', padx=5)
        self.filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # liste
        cols = ('vehicule', 'conducteur', 'sortie', 'retour', 'km', 'duree', 'statut')
        self.tree_hist = ttk.Treeview(tab, columns=cols, show='headings', height=12)
        self.tree_hist.heading('vehicule', text='Véhicule')
        self.tree_hist.heading('conducteur', text='Conducteur')
        self.tree_hist.heading('sortie', text='Sortie')
        self.tree_hist.heading('retour', text='Retour')
        self.tree_hist.heading('km', text='Km')
        self.tree_hist.heading('duree', text='Durée')
        self.tree_hist.heading('statut', text='Statut')
        
        # couleurs
        self.tree_hist.tag_configure('terminee', background='lightgreen')
        self.tree_hist.tag_configure('annulee', background='red')
        
        self.tree_hist.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh(self):
        # en cours
        self.tree_cours.delete(*self.tree_cours.get_children())
        for s in self.sortie_ctrl.get_en_cours():
            date_sortie = s.date_sortie_reelle or s.date_sortie_prevue
            self.tree_cours.insert('', 'end',
                values=(f"{s.immatriculation} ({s.marque})", f"{s.prenom} {s.nom}",
                       date_sortie, s.destination or '-', s.motif or '-',
                       f"{s.km_depart} km" if s.km_depart else '-'),
                tags=(str(s.id),))
        
        # historique
        self.tree_hist.delete(*self.tree_hist.get_children())
        statut = self.filter.get()
        statut = None if statut == 'Tous' else statut
        
        for s in self.sortie_ctrl.get_historique(statut):
            km = f"{s.km_parcourus} km" if s.km_parcourus else '-'
            
            # calculer durée
            duree = '-'
            if s.date_sortie_reelle and s.date_retour_reelle:
                try:
                    d1 = datetime.strptime(s.date_sortie_reelle, '%Y-%m-%d')
                    d2 = datetime.strptime(s.date_retour_reelle, '%Y-%m-%d')
                    days = (d2 - d1).days
                    duree = f"{days} j" if days > 1 else "1 j"
                except:
                    pass
            
            self.tree_hist.insert('', 'end',
                values=(f"{s.immatriculation}", f"{s.prenom} {s.nom}",
                       s.date_sortie_reelle or '-', s.date_retour_reelle or '-',
                       km, duree, s.statut),
                tags=(s.statut, str(s.id)))

    def new_sortie(self, veh_id=None):
        SortieForm(self, self.app, self.sortie_ctrl, self.veh_ctrl, self.emp_ctrl, veh_id, self.refresh)

    def retour(self):
        sel = self.tree_cours.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une sortie")
            return
        sid = int(self.tree_cours.item(sel[0], 'tags')[0])
        RetourForm(self, self.app, self.sortie_ctrl, sid, self.refresh)


class SortieForm(tk.Toplevel):
    def __init__(self, parent, app, ctrl, veh_ctrl, emp_ctrl, veh_id, cb):
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.cb = cb
        
        vehs = veh_ctrl.get_available()
        self.veh_dict = {f"{v.immatriculation} - {v.marque} {v.modele}": v.id for v in vehs}
        
        emps = emp_ctrl.get_authorized()
        self.emp_dict = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in emps}
        
        self.title("Nouvelle sortie")
        self.geometry("450x550")
        
        f = tk.Frame(self, bg='white', padx=20, pady=20)
        f.pack(fill='both', expand=True)
        
        # champs
        tk.Label(f, text="Véhicule *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.veh = ttk.Combobox(f, values=list(self.veh_dict.keys()), width=30)
        self.veh.grid(row=0, column=1, pady=5)
        
        tk.Label(f, text="Conducteur *", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.emp = ttk.Combobox(f, values=list(self.emp_dict.keys()), width=30)
        self.emp.grid(row=1, column=1, pady=5)
        
        tk.Label(f, text="Motif", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.motif = tk.Entry(f, width=32)
        self.motif.grid(row=2, column=1, pady=5)
        
        tk.Label(f, text="Destination", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.dest = tk.Entry(f, width=32)
        self.dest.grid(row=3, column=1, pady=5)
        
        tk.Label(f, text="Date sortie", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.date_sortie = tk.Entry(f, width=32)
        self.date_sortie.insert(0, date.today().isoformat())
        self.date_sortie.grid(row=4, column=1, pady=5)
        
        tk.Label(f, text="Heure sortie", bg='white').grid(row=5, column=0, sticky='w', pady=5)
        self.heure_sortie = tk.Entry(f, width=32)
        self.heure_sortie.insert(0, "08:00")
        self.heure_sortie.grid(row=5, column=1, pady=5)
        
        tk.Label(f, text="Date retour prévue", bg='white').grid(row=6, column=0, sticky='w', pady=5)
        self.date_retour = tk.Entry(f, width=32)
        self.date_retour.grid(row=6, column=1, pady=5)
        
        tk.Label(f, text="Heure retour", bg='white').grid(row=7, column=0, sticky='w', pady=5)
        self.heure_retour = tk.Entry(f, width=32)
        self.heure_retour.grid(row=7, column=1, pady=5)
        
        tk.Label(f, text="Km départ *", bg='white').grid(row=8, column=0, sticky='w', pady=5)
        self.km = tk.Entry(f, width=32)
        self.km.grid(row=8, column=1, pady=5)
        
        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', pady=10)
        tk.Button(btns, text="Enregistrer", command=self.save, bg='green', fg='white', width=12).pack(side='right', padx=20)
        tk.Button(btns, text="Annuler", command=self.destroy, bg='gray', fg='white', width=12).pack(side='right', padx=5)
        
        # présélection véhicule
        if veh_id:
            for k, v in self.veh_dict.items():
                if v == veh_id:
                    self.veh.set(k)
                    break
    
    def save(self):
        if not self.veh.get() or not self.emp.get() or not self.km.get():
            messagebox.showerror("Erreur", "Remplissez les champs obligatoires")
            return
        
        data = {
            'vehicule_id': self.veh_dict[self.veh.get()],
            'employe_id': self.emp_dict[self.emp.get()],
            'motif': self.motif.get() or None,
            'destination': self.dest.get() or None,
            'date_sortie_prevue': self.date_sortie.get(),
            'heure_sortie_prevue': self.heure_sortie.get(),
            'date_retour_prevue': self.date_retour.get() or None,
            'heure_retour_prevue': self.heure_retour.get() or None,
            'km_depart': self.km.get()
        }
        
        res = self.ctrl.create_sortie(data, self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Sortie enregistrée")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)


class RetourForm(tk.Toplevel):
    def __init__(self, parent, app, ctrl, sortie_id, cb):
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.sortie = ctrl.get_by_id(sortie_id)
        self.cb = cb
        
        self.title("Retour de véhicule")
        self.geometry("450x400")
        
        # infos sortie
        info = tk.Frame(self, bg='lightgray', padx=20, pady=15)
        info.pack(fill='x')
        tk.Label(info, text=f"Véhicule: {self.sortie.immatriculation} ({self.sortie.marque})", 
                font=('Arial', 10, 'bold'), bg='lightgray').pack(anchor='w')
        tk.Label(info, text=f"Conducteur: {self.sortie.prenom} {self.sortie.nom}", 
                bg='lightgray').pack(anchor='w')
        tk.Label(info, text=f"Km départ: {self.sortie.km_depart} km", 
                bg='lightgray').pack(anchor='w')
        
        # formulaire
        f = tk.Frame(self, bg='white', padx=20, pady=20)
        f.pack(fill='both', expand=True)
        
        tk.Label(f, text="Km retour *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.km = tk.Entry(f, width=30)
        self.km.grid(row=0, column=1, pady=5)
        
        tk.Label(f, text="État véhicule", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.etat = ttk.Combobox(f, values=['Bon', 'Sale', 'Endommagé'], width=28)
        self.etat.set('Bon')
        self.etat.grid(row=1, column=1, pady=5)
        
        tk.Label(f, text="Niveau carburant", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.carb = ttk.Combobox(f, values=['Plein', '3/4', '1/2', '1/4', 'Vide'], width=28)
        self.carb.set('3/4')
        self.carb.grid(row=2, column=1, pady=5)
        
        tk.Label(f, text="Nouveau statut", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.statut = ttk.Combobox(f, values=['disponible', 'en_maintenance', 'en_panne'], width=28)
        self.statut.set('disponible')
        self.statut.grid(row=3, column=1, pady=5)
        
        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', pady=10)
        tk.Button(btns, text="Valider retour", command=self.save, bg='green', fg='white', width=12).pack(side='right', padx=20)
        tk.Button(btns, text="Annuler", command=self.destroy, bg='gray', fg='white', width=12).pack(side='right', padx=5)
    
    def save(self):
        if not self.km.get():
            messagebox.showerror("Erreur", "Indiquez le kilométrage retour")
            return
        
        data = {
            'km_retour': self.km.get(),
            'etat_retour': self.etat.get(),
            'niveau_carburant': self.carb.get(),
            'nouveau_statut': self.statut.get()
        }
        
        res = self.ctrl.enregistrer_retour(self.sortie.id, data, self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Retour enregistré")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)