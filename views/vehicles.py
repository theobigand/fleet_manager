import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers import VehicleController


class VehiclesView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.ctrl = VehicleController()
        self.setup_vehicle()
        self.refresh()

    def setup_vehicle(self) -> None:
        # titre
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(top, text="Véhicules", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(side='left')
        ctk.CTkButton(top, text="+ Ajouter", command=self.add,
                      fg_color='#2ecc71', hover_color='#27ae60', width=100).pack(side='right')

        # filtre statut
        filter_frame = ctk.CTkFrame(self, fg_color='transparent')
        filter_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(filter_frame, text="Statut:", text_color='#333333').pack(side='left')
        self.filter = ctk.CTkComboBox(filter_frame, values=['Tous', 'disponible', 'en sortie', 'en maintenance'],
                                       width=150, command=lambda e: self.refresh())
        self.filter.set('Tous')
        self.filter.pack(side='left', padx=5)
        ctk.CTkButton(filter_frame, text="Actualiser", command=self.refresh,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='right')

        # alerte parc complet
        self.alert = ctk.CTkFrame(self, fg_color='#e74c3c', corner_radius=8)
        ctk.CTkLabel(self.alert, text="⚠️ PARC COMPLET - Aucun véhicule disponible",
                     font=ctk.CTkFont(size=14, weight='bold'), text_color='white').pack(pady=10)

        # liste (on garde ttk.Treeview pour les tableaux)
        tree_frame = ctk.CTkFrame(self, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        cols = ('immat', 'marque', 'modele', 'statut', 'km')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree.heading('immat', text='Immatriculation')
        self.tree.heading('marque', text='Marque')
        self.tree.heading('modele', text='Modèle')
        self.tree.heading('statut', text='Statut')
        self.tree.heading('km', text='Km')

        # couleurs
        self.tree.tag_configure('disponible', background='#d5f4e6')
        self.tree.tag_configure('en_sortie', background='#ffeaa7')
        self.tree.tag_configure('en_maintenance', background='#fab1a0')
        self.tree.tag_configure('en_panne', background='#ff7675')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', lambda e: self.detail())

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', padx=20, pady=10)
        ctk.CTkButton(btns, text="Détails", command=self.detail,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Modifier", command=self.edit,
                      fg_color='#f39c12', hover_color='#e67e22', width=100).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Supprimer", command=self.delete,
                      fg_color='#e74c3c', hover_color='#c0392b', width=100).pack(side='left', padx=5)

    def refresh(self) -> None:
        # vider
        for item in self.tree.get_children():
            self.tree.delete(item)

        # filtrer
        filter_value = self.filter.get()
        filters = None if filter_value == 'Tous' else {'statut': filter_value}

        # charger
        vehicles = self.ctrl.get_all(filters)
        dispo = 0

        for v in vehicles:
            if v.statut == 'disponible':
                dispo += 1
            self.tree.insert('', 'end',
                             values=(v.immatriculation, v.marque, v.modele, v.statut, f"{v.kilometrage_actuel} km"),
                             tags=(v.statut, str(v.id)))

        # Alerte
        if dispo == 0 and len(vehicles) > 0:
            self.alert.pack(fill='x', padx=20, pady=10, before=self.tree.master)
        else:
            self.alert.pack_forget()

    def add(self) -> None:
        VehiculeForm(self, self.app, self.ctrl, None, self.refresh)

    def edit(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un véhicule")
            return
        vid = int(self.tree.item(sel[0], 'tags')[1])
        veh = self.ctrl.get_by_id(vid)
        VehiculeForm(self, self.app, self.ctrl, veh, self.refresh)

    def delete(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un véhicule")
            return
        vid = int(self.tree.item(sel[0], 'tags')[1])
        veh = self.ctrl.get_by_id(vid)
        if not messagebox.askyesno("Confirmation", f"Supprimer {veh.immatriculation} ?"):
            return
        res = self.ctrl.delete(vid, self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Véhicule supprimé")
            self.refresh()
        else:
            messagebox.showerror("Erreur", res.message)

    def detail(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        vid = int(self.tree.item(sel[0], 'tags')[1])
        VehDetail(self, self.ctrl, vid)


class VehiculeForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, vehicle, callback) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.veh = vehicle
        self.cb = callback

        self.title("Modifier" if vehicle else "Nouveau véhicule")
        self.geometry("500x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        # Champs
        ctk.CTkLabel(f, text="Immatriculation *").grid(row=0, column=0, sticky='w', pady=8)
        self.immat = ctk.CTkEntry(f, width=280)
        self.immat.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="Marque *").grid(row=1, column=0, sticky='w', pady=8)
        self.marque = ctk.CTkEntry(f, width=280)
        self.marque.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Modèle *").grid(row=2, column=0, sticky='w', pady=8)
        self.modele = ctk.CTkEntry(f, width=280)
        self.modele.grid(row=2, column=1, pady=8)

        ctk.CTkLabel(f, text="Type").grid(row=3, column=0, sticky='w', pady=8)
        self.type = ctk.CTkComboBox(f, values=['Voiture', 'Utilitaire', 'Camionnette'], width=280)
        self.type.grid(row=3, column=1, pady=8)

        ctk.CTkLabel(f, text="Année").grid(row=4, column=0, sticky='w', pady=8)
        self.annee = ctk.CTkEntry(f, width=280)
        self.annee.grid(row=4, column=1, pady=8)

        ctk.CTkLabel(f, text="Kilométrage").grid(row=5, column=0, sticky='w', pady=8)
        self.km = ctk.CTkEntry(f, width=280)
        self.km.insert(0, "0")
        self.km.grid(row=5, column=1, pady=8)

        ctk.CTkLabel(f, text="Carburant").grid(row=6, column=0, sticky='w', pady=8)
        self.carb = ctk.CTkComboBox(f, values=['Essence', 'Diesel', 'Électrique'], width=280)
        self.carb.grid(row=6, column=1, pady=8)

        ctk.CTkLabel(f, text="Statut").grid(row=7, column=0, sticky='w', pady=8)
        self.statut = ctk.CTkComboBox(f, values=['disponible', 'en sortie', 'en maintenance'], width=280)
        self.statut.set('disponible')
        self.statut.grid(row=7, column=1, pady=8)

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

        # charger si modif
        if vehicle:
            self.immat.insert(0, vehicle.immatriculation)
            self.marque.insert(0, vehicle.marque)
            self.modele.insert(0, vehicle.modele)
            self.type.set(vehicle.type_vehicule or '')
            self.annee.insert(0, vehicle.annee or '')
            self.km.delete(0, 'end')
            self.km.insert(0, vehicle.kilometrage_actuel or 0)
            self.carb.set(vehicle.carburant or '')
            self.statut.set(vehicle.statut)

    def save(self) -> None:
        if not self.immat.get() or not self.marque.get() or not self.modele.get():
            messagebox.showerror("Erreur", "Remplissez les champs obligatoires")
            return

        data = {
            'immatriculation': self.immat.get(),
            'marque': self.marque.get(),
            'modele': self.modele.get(),
            'type_vehicule': self.type.get() or None,
            'annee': self.annee.get() or None,
            'kilometrage_actuel': int(self.km.get() or 0),
            'carburant': self.carb.get() or None,
            'statut': self.statut.get()
        }

        if self.veh:
            res = self.ctrl.update(self.veh.id, data, self.app.current_user.id)
        else:
            res = self.ctrl.create(data, self.app.current_user.id)

        if res.success:
            messagebox.showinfo("OK", "Enregistré")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)


class VehDetail(ctk.CTkToplevel):
    def __init__(self, parent, ctrl, vid) -> None:
        super().__init__(parent)
        v = ctrl.get_by_id(vid)

        self.title(f"Fiche - {v.immatriculation}")
        self.geometry("650x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # header
        h = ctk.CTkFrame(self, fg_color='#ecf0f1', corner_radius=0)
        h.pack(fill='x')
        ctk.CTkLabel(h, text=f"{v.immatriculation} - {v.marque} {v.modele}",
                     font=ctk.CTkFont(size=20, weight='bold'), text_color='#2c3e50').pack(pady=20, padx=20)

        # infos
        info = ctk.CTkFrame(self, fg_color='transparent')
        info.pack(fill='both', expand=True, padx=30, pady=20)

        infos = [
            ("Marque:", v.marque),
            ("Modèle:", v.modele),
            ("Type:", v.type_vehicule or '-'),
            ("Année:", v.annee or '-'),
            ("Km:", f"{v.kilometrage_actuel} km"),
            ("Carburant:", v.carburant or '-'),
            ("Statut:", v.statut)
        ]

        for i, (lbl, val) in enumerate(infos):
            ctk.CTkLabel(info, text=lbl, font=ctk.CTkFont(weight='bold'),
                         text_color='#7f8c8d').grid(row=i, column=0, sticky='e', padx=10, pady=8)
            ctk.CTkLabel(info, text=val, text_color='#2c3e50').grid(row=i, column=1, sticky='w', padx=10, pady=8)

        ctk.CTkButton(self, text="Fermer", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=120).pack(pady=15)