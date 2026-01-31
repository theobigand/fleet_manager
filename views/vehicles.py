import tkinter as tk
from tkinter import ttk, messagebox
from controllers import VehicleController


class VehiclesView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='white')
        self.app = app
        self.ctrl = VehicleController()
        self.setup_vehicle()
        self.refresh()

    def setup_vehicle(self):
        # titre
        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=20, pady=20)
        tk.Label(top, text="Véhicules", font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        tk.Button(top, text="+ Ajouter", command=self.add, bg='green', fg='white').pack(side='right')

        # filtre statut
        filter = tk.Frame(self, bg='white')
        filter.pack(fill='x', padx=20, pady=5)
        tk.Label(filter, text="Statut:", bg='white').pack(side='left')
        self.filter = ttk.Combobox(filter, values=['Tous', 'disponible', 'en sortie', 'en maintenance'], width=15)
        self.filter.set('Tous')
        self.filter.pack(side='left', padx=5)
        self.filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        tk.Button(filter, text="Actualiser", command=self.refresh, bg='blue', fg='white').pack(side='right')

        # alerte parc complet
        self.alert = tk.Frame(self, bg='red', pady=10)
        tk.Label(self.alert, text="⚠️ PARC COMPLET - Aucun véhicule disponible", 
                font=('Arial', 12, 'bold'), bg='red', fg='white').pack()

        # liste
        cols = ('immat', 'marque', 'modele', 'statut', 'km')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)
        self.tree.heading('immat', text='Immatriculation')
        self.tree.heading('marque', text='Marque')
        self.tree.heading('modele', text='Modèle')
        self.tree.heading('statut', text='Statut')
        self.tree.heading('km', text='Km')
        
        # couleurs
        self.tree.tag_configure('disponible', background='lightgreen')
        self.tree.tag_configure('en_sortie', background='yellow')
        self.tree.tag_configure('en_maintenance', background='orange')
        self.tree.tag_configure('en_panne', background='red')
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree.bind('<Double-1>', lambda e: self.detail())

        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', padx=20, pady=10)
        tk.Button(btns, text="Détails", command=self.detail, bg='blue', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text="Modifier", command=self.edit, bg='orange', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text="Supprimer", command=self.delete, bg='red', fg='white').pack(side='left', padx=5)

    def refresh(self):
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
            self.alert.pack(fill='x', padx=20, pady=10, before=self.tree)
        else:
            self.alert.pack_forget()

    def add(self):
        VehiculeForm(self, self.app, self.ctrl, None, self.refresh)

    def edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un véhicule")
            return
        vid = int(self.tree.item(sel[0], 'tags')[1])
        veh = self.ctrl.get_by_id(vid)
        VehiculeForm(self, self.app, self.ctrl, veh, self.refresh)

    def delete(self):
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

    def detail(self):
        sel = self.tree.selection()
        if not sel:
            return
        vid = int(self.tree.item(sel[0], 'tags')[1])
        VehDetail(self, self.ctrl, vid)


class VehiculeForm(tk.Toplevel):
    def __init__(self, parent, app, ctrl, vehicle, callback):
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.veh = vehicle
        self.cb = callback
        
        self.title("Modifier" if vehicle else "Nouveau véhicule")
        self.geometry("450x550")
        
        f = tk.Frame(self, bg='white', padx=20, pady=20)
        f.pack(fill='both', expand=True)
        
        # Champs
        tk.Label(f, text="Immatriculation *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.immat = tk.Entry(f, width=30)
        self.immat.grid(row=0, column=1, pady=5)
        
        tk.Label(f, text="Marque *", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.marque = tk.Entry(f, width=30)
        self.marque.grid(row=1, column=1, pady=5)
        
        tk.Label(f, text="Modèle *", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.modele = tk.Entry(f, width=30)
        self.modele.grid(row=2, column=1, pady=5)
        
        tk.Label(f, text="Type", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.type = ttk.Combobox(f, values=['Voiture', 'Utilitaire', 'Camionnette'], width=28)
        self.type.grid(row=3, column=1, pady=5)
        
        tk.Label(f, text="Année", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.annee = tk.Entry(f, width=30)
        self.annee.grid(row=4, column=1, pady=5)
        
        tk.Label(f, text="Kilométrage", bg='white').grid(row=5, column=0, sticky='w', pady=5)
        self.km = tk.Entry(f, width=30)
        self.km.insert(0, "0")
        self.km.grid(row=5, column=1, pady=5)
        
        tk.Label(f, text="Carburant", bg='white').grid(row=6, column=0, sticky='w', pady=5)
        self.carb = ttk.Combobox(f, values=['Essence', 'Diesel', 'Électrique'], width=28)
        self.carb.grid(row=6, column=1, pady=5)
        
        tk.Label(f, text="Statut", bg='white').grid(row=7, column=0, sticky='w', pady=5)
        self.statut = ttk.Combobox(f, values=['disponible', 'en sortie', 'en maintenance'], width=28)
        self.statut.set('disponible')
        self.statut.grid(row=7, column=1, pady=5)
        
        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', pady=10)
        tk.Button(btns, text="Enregistrer", command=self.save, bg='green', fg='white', width=12).pack(side='right', padx=20)
        tk.Button(btns, text="Annuler", command=self.destroy, bg='gray', fg='white', width=12).pack(side='right', padx=5)
        
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
    
    def save(self):
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


class VehDetail(tk.Toplevel):
    def __init__(self, parent, ctrl, vid):
        super().__init__(parent)
        v = ctrl.get_by_id(vid)
        
        self.title(f"Fiche - {v.immatriculation}")
        self.geometry("600x400")
        
        # header
        h = tk.Frame(self, bg='lightgray', pady=15)
        h.pack(fill='x')
        tk.Label(h, text=f"{v.immatriculation} - {v.marque} {v.modele}", 
                font=('Arial', 16, 'bold'), bg='lightgray').pack(padx=20)
        
        # infos
        info = tk.Frame(self, bg='white', padx=20, pady=20)
        info.pack(fill='both', expand=True)
        
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
            tk.Label(info, text=lbl, font=('Arial', 10, 'bold'), bg='white').grid(row=i, column=0, sticky='e', padx=5, pady=5)
            tk.Label(info, text=val, font=('Arial', 10), bg='white').grid(row=i, column=1, sticky='w', padx=5, pady=5)
        
        tk.Button(self, text="Fermer", command=self.destroy, bg='gray', fg='white').pack(pady=10)