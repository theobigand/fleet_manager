import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, date
from controllers import SortieController, VehicleController, EmployeeController


class ReservationsView(ctk.CTkFrame):
    def __init__(self, parent, app, vehicle_id=None) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.sortie_ctrl = SortieController()
        self.veh_ctrl = VehicleController()
        self.emp_ctrl = EmployeeController()
        self.preselect_veh = vehicle_id
        self.setup_reservation()
        self.refresh()

        if vehicle_id:
            self.after(100, lambda: self.new_sortie(vehicle_id))

    def setup_reservation(self) -> None:
        # titre
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(top, text="Réservations & Sorties", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(side='left')
        ctk.CTkButton(top, text="+ Nouvelle sortie", command=lambda: self.new_sortie(),
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right')

        # onglets
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=20, pady=10)

        self.create_tab_en_cours()
        self.create_tab_historique()

    def create_tab_en_cours(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='En cours')

        ctk.CTkLabel(tab, text="Double-clic pour enregistrer le retour",
                     font=ctk.CTkFont(size=11, slant='italic'), text_color='gray').pack(anchor='w', padx=10, pady=5)

        # liste
        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('vehicule', 'conducteur', 'date', 'destination', 'motif', 'km')
        self.tree_cours = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        self.tree_cours.heading('vehicule', text='Véhicule')
        self.tree_cours.heading('conducteur', text='Conducteur')
        self.tree_cours.heading('date', text='Date sortie')
        self.tree_cours.heading('destination', text='Destination')
        self.tree_cours.heading('motif', text='Motif')
        self.tree_cours.heading('km', text='Km départ')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_cours.yview)
        self.tree_cours.configure(yscrollcommand=scrollbar.set)
        self.tree_cours.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree_cours.bind('<Double-1>', lambda e: self.retour())

    def create_tab_historique(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Historique')

        # filtre
        flt = ctk.CTkFrame(tab, fg_color='transparent')
        flt.pack(fill='x', padx=10, pady=10)
        ctk.CTkLabel(flt, text="Statut:", text_color='#333333').pack(side='left')
        self.filter = ctk.CTkComboBox(flt, values=['Tous', 'terminee', 'annulee'], width=150,
                                       command=lambda e: self.refresh())
        self.filter.set('Tous')
        self.filter.pack(side='left', padx=5)

        # liste
        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('vehicule', 'conducteur', 'sortie', 'retour', 'km', 'duree', 'statut')
        self.tree_hist = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        self.tree_hist.heading('vehicule', text='Véhicule')
        self.tree_hist.heading('conducteur', text='Conducteur')
        self.tree_hist.heading('sortie', text='Sortie')
        self.tree_hist.heading('retour', text='Retour')
        self.tree_hist.heading('km', text='Km')
        self.tree_hist.heading('duree', text='Durée')
        self.tree_hist.heading('statut', text='Statut')

        # couleurs
        self.tree_hist.tag_configure('terminee', background='#d5f4e6')
        self.tree_hist.tag_configure('annulee', background='#ff7675')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=scrollbar.set)
        self.tree_hist.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def refresh(self) -> None:
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

    def new_sortie(self, veh_id=None) -> None:
        SortieForm(self, self.app, self.sortie_ctrl, self.veh_ctrl, self.emp_ctrl, veh_id, self.refresh)

    def retour(self) -> None:
        sel = self.tree_cours.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une sortie")
            return
        sid = int(self.tree_cours.item(sel[0], 'tags')[0])
        RetourForm(self, self.app, self.sortie_ctrl, sid, self.refresh)


class SortieForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, veh_ctrl, emp_ctrl, veh_id, cb) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.cb = cb

        vehs = veh_ctrl.get_available()
        self.veh_dict = {f"{v.immatriculation} - {v.marque} {v.modele}": v.id for v in vehs}

        emps = emp_ctrl.get_authorized()
        self.emp_dict = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in emps}

        self.title("Nouvelle sortie")
        self.geometry("500x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        # champs
        ctk.CTkLabel(f, text="Véhicule *").grid(row=0, column=0, sticky='w', pady=8)
        self.veh = ctk.CTkComboBox(f, values=list(self.veh_dict.keys()), width=300)
        self.veh.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="Conducteur *").grid(row=1, column=0, sticky='w', pady=8)
        self.emp = ctk.CTkComboBox(f, values=list(self.emp_dict.keys()), width=300)
        self.emp.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Motif").grid(row=2, column=0, sticky='w', pady=8)
        self.motif = ctk.CTkEntry(f, width=300)
        self.motif.grid(row=2, column=1, pady=8)

        ctk.CTkLabel(f, text="Destination").grid(row=3, column=0, sticky='w', pady=8)
        self.dest = ctk.CTkEntry(f, width=300)
        self.dest.grid(row=3, column=1, pady=8)

        ctk.CTkLabel(f, text="Date sortie").grid(row=4, column=0, sticky='w', pady=8)
        self.date_sortie = ctk.CTkEntry(f, width=300)
        self.date_sortie.insert(0, date.today().isoformat())
        self.date_sortie.grid(row=4, column=1, pady=8)

        ctk.CTkLabel(f, text="Heure sortie").grid(row=5, column=0, sticky='w', pady=8)
        self.heure_sortie = ctk.CTkEntry(f, width=300)
        self.heure_sortie.insert(0, "08:00")
        self.heure_sortie.grid(row=5, column=1, pady=8)

        ctk.CTkLabel(f, text="Date retour prévue").grid(row=6, column=0, sticky='w', pady=8)
        self.date_retour = ctk.CTkEntry(f, width=300)
        self.date_retour.grid(row=6, column=1, pady=8)

        ctk.CTkLabel(f, text="Heure retour").grid(row=7, column=0, sticky='w', pady=8)
        self.heure_retour = ctk.CTkEntry(f, width=300)
        self.heure_retour.grid(row=7, column=1, pady=8)

        ctk.CTkLabel(f, text="Km départ *").grid(row=8, column=0, sticky='w', pady=8)
        self.km = ctk.CTkEntry(f, width=300)
        self.km.grid(row=8, column=1, pady=8)

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

        # présélection véhicule
        if veh_id:
            for k, v in self.veh_dict.items():
                if v == veh_id:
                    self.veh.set(k)
                    break

    def save(self) -> None:
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


class RetourForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, sortie_id, cb) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.sortie = ctrl.get_by_id(sortie_id)
        self.cb = cb

        self.title("Retour de véhicule")
        self.geometry("500x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # infos sortie
        info = ctk.CTkFrame(self, fg_color='#ecf0f1', corner_radius=0)
        info.pack(fill='x')
        ctk.CTkLabel(info, text=f"Véhicule: {self.sortie.immatriculation} ({self.sortie.marque})",
                     font=ctk.CTkFont(size=13, weight='bold'), text_color='#2c3e50').pack(anchor='w', padx=20, pady=(15, 5))
        ctk.CTkLabel(info, text=f"Conducteur: {self.sortie.prenom} {self.sortie.nom}",
                     text_color='#2c3e50').pack(anchor='w', padx=20, pady=2)
        ctk.CTkLabel(info, text=f"Km départ: {self.sortie.km_depart} km",
                     text_color='#2c3e50').pack(anchor='w', padx=20, pady=(2, 15))

        # formulaire
        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text="Km retour *").grid(row=0, column=0, sticky='w', pady=8)
        self.km = ctk.CTkEntry(f, width=280)
        self.km.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="État véhicule").grid(row=1, column=0, sticky='w', pady=8)
        self.etat = ctk.CTkComboBox(f, values=['Bon', 'Sale', 'Endommagé'], width=280)
        self.etat.set('Bon')
        self.etat.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Niveau carburant").grid(row=2, column=0, sticky='w', pady=8)
        self.carb = ctk.CTkComboBox(f, values=['Plein', '3/4', '1/2', '1/4', 'Vide'], width=280)
        self.carb.set('3/4')
        self.carb.grid(row=2, column=1, pady=8)

        ctk.CTkLabel(f, text="Nouveau statut").grid(row=3, column=0, sticky='w', pady=8)
        self.statut = ctk.CTkComboBox(f, values=['disponible', 'en_maintenance', 'en_panne'], width=280)
        self.statut.set('disponible')
        self.statut.grid(row=3, column=1, pady=8)

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Valider retour", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

    def save(self) -> None:
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