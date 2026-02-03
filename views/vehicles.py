import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from controllers import VehicleController
from widgets import SearchBar, AlertBanner
from config import (VEHICLE_STATUSES, AFFECTATION_TYPES, format_status,
                    format_affectation, get_status_key, get_affectation_key)


class VehiclesView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.ctrl = VehicleController()
        self.setup_vehicle()
        self.refresh()

    def setup_vehicle(self) -> None:
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(top, text="Véhicules", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(side='left')
        ctk.CTkButton(top, text="+ Ajouter", command=self.add,
                      fg_color='#2ecc71', hover_color='#27ae60', width=100).pack(side='right')

        self.search_bar = SearchBar(
            self,
            on_search=self.refresh,
            filters=[
                ('Statut', 'statut', ['Disponible', 'En sortie', 'En maintenance', 'En panne']),
                ('Type', 'type', ['Voiture', 'Utilitaire', 'Camionnette', 'Citadine', 'Berline']),
                ('Affectation', 'affectation', ['Mutualisé', 'Voiture de fonction'])
            ],
            placeholder="immat, marque..."
        )
        self.search_bar.pack(fill='x', padx=20, pady=5)

        self.statut_map = {'Disponible': 'disponible', 'En sortie': 'en_sortie',
                          'En maintenance': 'en_maintenance', 'En panne': 'en_panne'}
        self.affectation_map = {'Mutualisé': 'mutualise', 'Voiture de fonction': 'voiture_fonction'}

        self.alert = AlertBanner(self, "PARC COMPLET - Aucun véhicule disponible")

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
        for item in self.tree.get_children():
            self.tree.delete(item)

        filters = {}
        search = self.search_bar.get_search()
        if search:
            filters['search'] = search

        statut = self.search_bar.get_filter('statut')
        if statut:
            filters['statut'] = self.statut_map.get(statut, statut)

        type_v = self.search_bar.get_filter('type')
        if type_v:
            filters['type_vehicule'] = type_v

        affectation = self.search_bar.get_filter('affectation')
        if affectation:
            filters['type_affectation'] = self.affectation_map.get(affectation, affectation)

        vehicles = self.ctrl.get_all(filters if filters else None)
        dispo = 0

        for v in vehicles:
            if v.statut == 'disponible':
                dispo += 1
            self.tree.insert('', 'end',
                             values=(v.immatriculation, v.marque, v.modele, format_status(v.statut), f"{v.kilometrage_actuel} km"),
                             tags=(v.statut, str(v.id)))

        if dispo == 0 and len(vehicles) > 0:
            self.alert.show(before=self.tree.master)
        else:
            self.alert.hide()

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
        self.geometry("550x750")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

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
        self.type = ctk.CTkComboBox(f, values=['', 'Voiture', 'Utilitaire', 'Camionnette', 'Citadine', 'Berline'], width=280)
        self.type.grid(row=3, column=1, pady=8)

        ctk.CTkLabel(f, text="Année").grid(row=4, column=0, sticky='w', pady=8)
        self.annee = ctk.CTkEntry(f, width=280)
        self.annee.grid(row=4, column=1, pady=8)

        ctk.CTkLabel(f, text="Kilométrage").grid(row=5, column=0, sticky='w', pady=8)
        self.km = ctk.CTkEntry(f, width=280)
        self.km.insert(0, "0")
        self.km.grid(row=5, column=1, pady=8)

        ctk.CTkLabel(f, text="Carburant").grid(row=6, column=0, sticky='w', pady=8)
        self.carb = ctk.CTkComboBox(f, values=['', 'Essence', 'Diesel', 'Électrique', 'Hybride'], width=280)
        self.carb.grid(row=6, column=1, pady=8)

        ctk.CTkLabel(f, text="Statut").grid(row=7, column=0, sticky='w', pady=8)
        self.statut = ctk.CTkComboBox(f, values=list(VEHICLE_STATUSES.values()), width=280)
        self.statut.set('Disponible')
        self.statut.grid(row=7, column=1, pady=8)

        ctk.CTkLabel(f, text="Date acquisition").grid(row=8, column=0, sticky='w', pady=8)
        self.date_acq = ctk.CTkEntry(f, width=280, placeholder_text="AAAA-MM-JJ")
        self.date_acq.grid(row=8, column=1, pady=8)

        ctk.CTkLabel(f, text="Puissance fiscale").grid(row=9, column=0, sticky='w', pady=8)
        self.puissance = ctk.CTkEntry(f, width=280)
        self.puissance.grid(row=9, column=1, pady=8)

        ctk.CTkLabel(f, text="N° Châssis").grid(row=10, column=0, sticky='w', pady=8)
        self.chassis = ctk.CTkEntry(f, width=280)
        self.chassis.grid(row=10, column=1, pady=8)

        ctk.CTkLabel(f, text="Service principal").grid(row=11, column=0, sticky='w', pady=8)
        self.service = ctk.CTkComboBox(f, values=['', 'Commercial', 'Technique', 'Administratif', 'Direction', 'Logistique'], width=280)
        self.service.grid(row=11, column=1, pady=8)

        ctk.CTkLabel(f, text="Type affectation").grid(row=12, column=0, sticky='w', pady=8)
        # Filtrer pour ne pas avoir de doublons (fonction est un alias)
        aff_values = [v for k, v in AFFECTATION_TYPES.items() if k != 'fonction']
        self.type_aff = ctk.CTkComboBox(f, values=aff_values, width=280)
        self.type_aff.set('Mutualisé')
        self.type_aff.grid(row=12, column=1, pady=8)

        ctk.CTkLabel(f, text="Seuil révision (km)").grid(row=13, column=0, sticky='w', pady=8)
        self.seuil = ctk.CTkEntry(f, width=280)
        self.seuil.insert(0, "15000")
        self.seuil.grid(row=13, column=1, pady=8)

        ctk.CTkLabel(f, text="Photo").grid(row=14, column=0, sticky='w', pady=8)
        photo_frame = ctk.CTkFrame(f, fg_color='transparent')
        photo_frame.grid(row=14, column=1, pady=8, sticky='w')
        self.photo = ctk.CTkEntry(photo_frame, width=200)
        self.photo.pack(side='left')
        ctk.CTkButton(photo_frame, text="...", width=30, command=self.browse_photo).pack(side='left', padx=5)

        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

        if vehicle:
            self.immat.insert(0, vehicle.immatriculation)
            self.marque.insert(0, vehicle.marque)
            self.modele.insert(0, vehicle.modele)
            self.type.set(vehicle.type_vehicule or '')
            self.annee.insert(0, vehicle.annee or '')
            self.km.delete(0, 'end')
            self.km.insert(0, vehicle.kilometrage_actuel or 0)
            self.carb.set(vehicle.carburant or '')
            self.statut.set(format_status(vehicle.statut))
            self.date_acq.insert(0, vehicle.date_acquisition or '')
            self.puissance.insert(0, str(vehicle.puissance_fiscale) if vehicle.puissance_fiscale else '')
            self.chassis.insert(0, vehicle.numero_chassis or '')
            self.service.set(vehicle.service_principal or '')
            self.type_aff.set(format_affectation(vehicle.type_affectation) if vehicle.type_affectation else 'Mutualisé')
            self.seuil.delete(0, 'end')
            self.seuil.insert(0, str(vehicle.seuil_revision_km) if vehicle.seuil_revision_km else '15000')
            self.photo.insert(0, vehicle.photo_path or '')

    def browse_photo(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            self.photo.delete(0, 'end')
            self.photo.insert(0, path)

    def save(self) -> None:
        if not self.immat.get() or not self.marque.get() or not self.modele.get():
            messagebox.showerror("Erreur", "Remplissez les champs obligatoires")
            return

        data = {
            'immatriculation': self.immat.get(),
            'marque': self.marque.get(),
            'modele': self.modele.get(),
            'type_vehicule': self.type.get() or None,
            'annee': int(self.annee.get()) if self.annee.get() else None,
            'kilometrage_actuel': int(self.km.get() or 0),
            'carburant': self.carb.get() or None,
            'statut': get_status_key(self.statut.get()),
            'date_acquisition': self.date_acq.get() or None,
            'puissance_fiscale': int(self.puissance.get()) if self.puissance.get() else None,
            'numero_chassis': self.chassis.get() or None,
            'service_principal': self.service.get() or None,
            'type_affectation': get_affectation_key(self.type_aff.get()) or 'mutualise',
            'seuil_revision_km': int(self.seuil.get()) if self.seuil.get() else 15000,
            'photo_path': self.photo.get() or None
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
        self.ctrl = ctrl
        self.v = ctrl.get_by_id(vid)

        self.title(f"Fiche - {self.v.immatriculation}")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        h = ctk.CTkFrame(self, fg_color='#ecf0f1', corner_radius=0)
        h.pack(fill='x')
        ctk.CTkLabel(h, text=f"{self.v.immatriculation} - {self.v.marque} {self.v.modele}",
                     font=ctk.CTkFont(size=20, weight='bold'), text_color='#2c3e50').pack(side='left', pady=20, padx=20)

        colors = {'disponible': '#2ecc71', 'en_sortie': '#f39c12', 'en_maintenance': '#e74c3c', 'en_panne': '#c0392b'}
        ctk.CTkLabel(h, text=format_status(self.v.statut), fg_color=colors.get(self.v.statut, '#95a5a6'),
                     corner_radius=6, text_color='white', padx=15, pady=5).pack(side='right', padx=20, pady=20)

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill='both', expand=True, padx=20, pady=10)

        tab_info = tabs.add("Informations")
        self.build_info_tab(tab_info)

        tab_sorties = tabs.add("Sorties")
        self.build_sorties_tab(tab_sorties)

        tab_maint = tabs.add("Maintenances")
        self.build_maint_tab(tab_maint)

        tab_fuel = tabs.add("Carburant")
        self.build_fuel_tab(tab_fuel)

        tab_docs = tabs.add("Documents")
        self.build_docs_tab(tab_docs)

        ctk.CTkButton(self, text="Fermer", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=120).pack(pady=15)

    def build_info_tab(self, parent) -> None:
        affectation = self.ctrl.dao.get_affectation(self.v.id)
        if affectation:
            aff_frame = ctk.CTkFrame(parent, fg_color='#e8f4f8', corner_radius=8)
            aff_frame.pack(fill='x', padx=10, pady=10)
            ctk.CTkLabel(aff_frame, text=f"Voiture de fonction: {affectation['prenom']} {affectation['nom']} ({affectation['matricule']})",
                         font=ctk.CTkFont(weight='bold')).pack(pady=10)

        conso = self.ctrl.dao.calculate_consumption(self.v.id)

        info = ctk.CTkFrame(parent, fg_color='transparent')
        info.pack(fill='both', expand=True, padx=10, pady=10)

        infos = [
            ("Immatriculation:", self.v.immatriculation),
            ("Marque:", self.v.marque),
            ("Modèle:", self.v.modele),
            ("Type:", self.v.type_vehicule or '-'),
            ("Année:", self.v.annee or '-'),
            ("Kilométrage:", f"{self.v.kilometrage_actuel} km"),
            ("Carburant:", self.v.carburant or '-'),
            ("Puissance fiscale:", f"{self.v.puissance_fiscale} CV" if self.v.puissance_fiscale else '-'),
            ("N° Châssis:", self.v.numero_chassis or '-'),
            ("Date acquisition:", self.v.date_acquisition or '-'),
            ("Service:", self.v.service_principal or '-'),
            ("Type affectation:", format_affectation(self.v.type_affectation) if self.v.type_affectation else '-'),
            ("Seuil révision:", f"{self.v.seuil_revision_km} km" if self.v.seuil_revision_km else '-'),
            ("Consommation moy.:", f"{conso} L/100km" if conso else '-'),
        ]

        for i, (lbl, val) in enumerate(infos):
            row, col = i // 2, (i % 2) * 2
            ctk.CTkLabel(info, text=lbl, font=ctk.CTkFont(weight='bold'),
                         text_color='#7f8c8d').grid(row=row, column=col, sticky='e', padx=10, pady=5)
            ctk.CTkLabel(info, text=str(val), text_color='#2c3e50').grid(row=row, column=col+1, sticky='w', padx=10, pady=5)

    def build_sorties_tab(self, parent) -> None:
        sorties = self.ctrl.dao.get_sorties(self.v.id)
        cols = ('date', 'employe', 'destination', 'km')
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=10)
        tree.heading('date', text='Date')
        tree.heading('employe', text='Conducteur')
        tree.heading('destination', text='Destination')
        tree.heading('km', text='Km parcourus')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        for s in sorties:
            km = (s.get('km_retour', 0) or 0) - (s.get('km_depart', 0) or 0)
            tree.insert('', 'end', values=(
                s.get('date_sortie_reelle', '-'),
                f"{s['prenom']} {s['nom']}",
                s.get('destination', '-'),
                f"{km} km" if km > 0 else '-'
            ))

    def build_maint_tab(self, parent) -> None:
        maints = self.ctrl.dao.get_maintenances(self.v.id)
        cols = ('date', 'type', 'km', 'cout', 'prestataire')
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=10)
        tree.heading('date', text='Date')
        tree.heading('type', text='Type')
        tree.heading('km', text='Kilométrage')
        tree.heading('cout', text='Coût')
        tree.heading('prestataire', text='Prestataire')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        for m in maints:
            tree.insert('', 'end', values=(
                m.get('date', '-'),
                m.get('type_intervention', '-'),
                f"{m.get('kilometrage', 0)} km",
                f"{m.get('cout', 0)} EUR",
                m.get('prestataire', '-')
            ))

    def build_fuel_tab(self, parent) -> None:
        ravit = self.ctrl.dao.get_ravitaillements(self.v.id)
        cols = ('date', 'litres', 'cout', 'station', 'km')
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=10)
        tree.heading('date', text='Date')
        tree.heading('litres', text='Quantité')
        tree.heading('cout', text='Coût')
        tree.heading('station', text='Station')
        tree.heading('km', text='Kilométrage')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        for r in ravit:
            tree.insert('', 'end', values=(
                r.get('date', '-'),
                f"{r.get('quantite_litres', 0)} L",
                f"{r.get('cout', 0)} EUR",
                r.get('station', '-'),
                f"{r.get('kilometrage', 0)} km"
            ))

    def build_docs_tab(self, parent) -> None:
        docs = self.ctrl.dao.get_documents(self.v.id)
        cols = ('type', 'emission', 'echeance', 'fichier')
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=10)
        tree.heading('type', text='Type')
        tree.heading('emission', text='Emission')
        tree.heading('echeance', text='Echéance')
        tree.heading('fichier', text='Fichier')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        for d in docs:
            tree.insert('', 'end', values=(
                d.get('type_document', '-'),
                d.get('date_emission', '-'),
                d.get('date_echeance', '-'),
                d.get('chemin_fichier', '-')
            ))