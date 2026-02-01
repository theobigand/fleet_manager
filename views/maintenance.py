import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
from controllers import MaintenanceController, VehicleController, EmployeeController, StatsController


class MaintenanceView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.maint_ctrl = MaintenanceController()
        self.veh_ctrl = VehicleController()
        self.emp_ctrl = EmployeeController()
        self.stats_ctrl = StatsController()
        self.setup_maintenance()
        self.refresh()

    def setup_maintenance(self) -> None:
        # titre
        ctk.CTkLabel(self, text="Maintenance & Carburant", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(pady=20)

        # onglets
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=20, pady=10)

        self.create_maint_tab()
        self.create_fuel_tab()
        self.create_alert_tab()

    def create_maint_tab(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Maintenance')

        # bouton ajouter
        ctk.CTkButton(tab, text="+ Intervention", command=self.add_maint,
                      fg_color='#2ecc71', hover_color='#27ae60', width=120).pack(anchor='e', padx=10, pady=10)

        # filtres
        flt = ctk.CTkFrame(tab, fg_color='transparent')
        flt.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(flt, text="Véhicule:", text_color='#333333').pack(side='left')
        vehs = self.veh_ctrl.get_all()
        self.filter_veh = ctk.CTkComboBox(flt, values=['Tous'] + [v.immatriculation for v in vehs],
                                           width=150, command=lambda e: self.refresh())
        self.filter_veh.set('Tous')
        self.filter_veh.pack(side='left', padx=5)

        ctk.CTkLabel(flt, text="Type:", text_color='#333333').pack(side='left', padx=10)
        types = ['Vidange', 'Pneus', 'Freins', 'Réparation', 'Contrôle technique']
        self.filter_type = ctk.CTkComboBox(flt, values=['Tous'] + types,
                                            width=150, command=lambda e: self.refresh())
        self.filter_type.set('Tous')
        self.filter_type.pack(side='left', padx=5)

        # liste
        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('date', 'vehicule', 'type', 'km', 'cout', 'prestataire')
        self.tree_maint = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        self.tree_maint.heading('date', text='Date')
        self.tree_maint.heading('vehicule', text='Véhicule')
        self.tree_maint.heading('type', text='Type')
        self.tree_maint.heading('km', text='Km')
        self.tree_maint.heading('cout', text='Coût')
        self.tree_maint.heading('prestataire', text='Prestataire')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_maint.yview)
        self.tree_maint.configure(yscrollcommand=scrollbar.set)
        self.tree_maint.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # boutons
        btns = ctk.CTkFrame(tab, fg_color='transparent')
        btns.pack(fill='x', padx=10, pady=10)
        ctk.CTkButton(btns, text="Modifier", command=self.edit_maint,
                      fg_color='#f39c12', hover_color='#e67e22', width=100).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Supprimer", command=self.del_maint,
                      fg_color='#e74c3c', hover_color='#c0392b', width=100).pack(side='left', padx=5)

    def create_fuel_tab(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Carburant')

        # bouton
        ctk.CTkButton(tab, text="+ Ravitaillement", command=self.add_fuel,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(anchor='e', padx=10, pady=10)

        # filtre
        flt = ctk.CTkFrame(tab, fg_color='transparent')
        flt.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(flt, text="Véhicule:", text_color='#333333').pack(side='left')
        vehs = self.veh_ctrl.get_all()
        self.filter_fuel = ctk.CTkComboBox(flt, values=['Tous'] + [v.immatriculation for v in vehs],
                                            width=150, command=lambda e: self.refresh())
        self.filter_fuel.set('Tous')
        self.filter_fuel.pack(side='left', padx=5)

        # liste
        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('date', 'vehicule', 'employe', 'litres', 'cout', 'station')
        self.tree_fuel = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        self.tree_fuel.heading('date', text='Date')
        self.tree_fuel.heading('vehicule', text='Véhicule')
        self.tree_fuel.heading('employe', text='Employé')
        self.tree_fuel.heading('litres', text='Litres')
        self.tree_fuel.heading('cout', text='Coût')
        self.tree_fuel.heading('station', text='Station')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_fuel.yview)
        self.tree_fuel.configure(yscrollcommand=scrollbar.set)
        self.tree_fuel.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # boutons
        ctk.CTkButton(tab, text="Supprimer", command=self.del_fuel,
                      fg_color='#e74c3c', hover_color='#c0392b', width=100).pack(anchor='e', padx=10, pady=10)

    def create_alert_tab(self):
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Échéances')

        ctk.CTkLabel(tab, text="Toutes les échéances à venir",
                     font=ctk.CTkFont(size=11, slant='italic'), text_color='gray').pack(anchor='w', padx=10, pady=10)

        # liste
        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('type', 'element', 'echeance', 'jours', 'statut')
        self.tree_alert = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree_alert.heading('type', text='Type')
        self.tree_alert.heading('element', text='Élément')
        self.tree_alert.heading('echeance', text='Échéance')
        self.tree_alert.heading('jours', text='Jours')
        self.tree_alert.heading('statut', text='Statut')

        # couleurs
        self.tree_alert.tag_configure('ok', background='#d5f4e6')
        self.tree_alert.tag_configure('warning', background='#ffeaa7')
        self.tree_alert.tag_configure('expired', background='#ff7675')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_alert.yview)
        self.tree_alert.configure(yscrollcommand=scrollbar.set)
        self.tree_alert.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def refresh(self) -> None:
        # maintenance
        self.tree_maint.delete(*self.tree_maint.get_children())
        veh = self.filter_veh.get()
        typ = self.filter_type.get()
        veh = None if veh == 'Tous' else veh
        typ = None if typ == 'Tous' else typ

        for m in self.maint_ctrl.get_all_maintenances(veh, typ):
            cout = f"{m.cout:.2f} €" if m.cout else '-'
            self.tree_maint.insert('', 'end',
                                   values=(m.date, f"{m.immatriculation}", m.type_intervention,
                                           f"{m.kilometrage} km" if m.kilometrage else '-', cout, m.prestataire or '-'),
                                   tags=(str(m.id),))

        # carburant
        self.tree_fuel.delete(*self.tree_fuel.get_children())
        veh2 = self.filter_fuel.get()
        veh2 = None if veh2 == 'Tous' else veh2

        for r in self.maint_ctrl.get_all_ravitaillements(veh2):
            emp = f"{r.prenom} {r.nom}" if r.prenom else '-'
            cout = f"{r.cout:.2f} €" if r.cout else '-'
            self.tree_fuel.insert('', 'end',
                                  values=(r.date, f"{r.immatriculation}", emp, f"{r.quantite_litres:.1f} L",
                                          cout, r.station or '-'),
                                  tags=(str(r.id),))

        # échéances
        self.tree_alert.delete(*self.tree_alert.get_children())
        for e in self.stats_ctrl.get_all_echeances():
            days = e.get('jours_restants')

            if days is not None and days < 0:
                tag = 'expired'
                statut = 'DÉPASSÉ'
            elif days is not None and days < 30:
                tag = 'warning'
                statut = f'{days} jours'
            else:
                tag = 'ok'
                statut = f'{days} jours' if days else '-'

            self.tree_alert.insert('', 'end',
                                   values=(e['type'], e['element'], e['date_echeance'] or '-',
                                           days if days is not None else '-', statut),
                                   tags=(tag,))

    def add_maint(self) -> None:
        MaintForm(self, self.app, self.maint_ctrl, self.veh_ctrl, None, self.refresh)

    def edit_maint(self) -> None:
        sel = self.tree_maint.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une intervention")
            return
        mid = int(self.tree_maint.item(sel[0], 'tags')[0])
        m = self.maint_ctrl.get_maintenance_by_id(mid)
        MaintForm(self, self.app, self.maint_ctrl, self.veh_ctrl, m, self.refresh)

    def del_maint(self) -> None:
        sel = self.tree_maint.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une intervention")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ?"):
            return
        mid = int(self.tree_maint.item(sel[0], 'tags')[0])
        self.maint_ctrl.delete_maintenance(mid, self.app.current_user.id)
        self.refresh()

    def add_fuel(self) -> None:
        FuelForm(self, self.app, self.maint_ctrl, self.veh_ctrl, self.emp_ctrl, self.refresh)

    def del_fuel(self) -> None:
        sel = self.tree_fuel.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un ravitaillement")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ?"):
            return
        rid = int(self.tree_fuel.item(sel[0], 'tags')[0])
        self.maint_ctrl.delete_ravitaillement(rid, self.app.current_user.id)
        self.refresh()


class MaintForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, veh_ctrl, maint, cb) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.maint = maint
        self.cb = cb

        vehs = veh_ctrl.get_all()
        self.veh_dict = {f"{v.immatriculation} - {v.marque}": v.id for v in vehs}

        self.title("Modifier" if maint else "Nouvelle intervention")
        self.geometry("500x580")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        # champs
        ctk.CTkLabel(f, text="Véhicule *").grid(row=0, column=0, sticky='w', pady=8)
        self.veh = ctk.CTkComboBox(f, values=list(self.veh_dict.keys()), width=300)
        self.veh.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="Date *").grid(row=1, column=0, sticky='w', pady=8)
        self.date = ctk.CTkEntry(f, width=300)
        self.date.insert(0, date.today().isoformat())
        self.date.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Type *").grid(row=2, column=0, sticky='w', pady=8)
        types = ['Vidange', 'Pneus', 'Freins', 'Réparation', 'Contrôle technique']
        self.type = ctk.CTkComboBox(f, values=types, width=300)
        self.type.grid(row=2, column=1, pady=8)

        ctk.CTkLabel(f, text="Kilométrage").grid(row=3, column=0, sticky='w', pady=8)
        self.km = ctk.CTkEntry(f, width=300)
        self.km.grid(row=3, column=1, pady=8)

        ctk.CTkLabel(f, text="Coût (€)").grid(row=4, column=0, sticky='w', pady=8)
        self.cout = ctk.CTkEntry(f, width=300)
        self.cout.grid(row=4, column=1, pady=8)

        ctk.CTkLabel(f, text="Prestataire").grid(row=5, column=0, sticky='w', pady=8)
        self.prest = ctk.CTkEntry(f, width=300)
        self.prest.grid(row=5, column=1, pady=8)

        ctk.CTkLabel(f, text="Remarques").grid(row=6, column=0, sticky='nw', pady=8)
        self.rem = ctk.CTkTextbox(f, width=300, height=80)
        self.rem.grid(row=6, column=1, pady=8)

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

        # charger
        if maint:
            for k, v in self.veh_dict.items():
                if v == maint.vehicule_id:
                    self.veh.set(k)
                    break
            self.date.delete(0, 'end')
            self.date.insert(0, maint.date or '')
            self.type.set(maint.type_intervention or '')
            self.km.insert(0, maint.kilometrage or '')
            self.cout.insert(0, maint.cout or '')
            self.prest.insert(0, maint.prestataire or '')
            self.rem.insert('1.0', maint.remarques or '')

    def save(self) -> None:
        if not self.veh.get() or not self.date.get() or not self.type.get():
            messagebox.showerror("Erreur", "Remplissez les champs obligatoires")
            return

        data = {
            'vehicule_id': self.veh_dict[self.veh.get()],
            'date': self.date.get(),
            'type_intervention': self.type.get(),
            'kilometrage': self.km.get() or None,
            'cout': self.cout.get() or None,
            'prestataire': self.prest.get() or None,
            'remarques': self.rem.get('1.0', 'end').strip() or None
        }

        if self.maint:
            res = self.ctrl.update_maintenance(self.maint.id, data, self.app.current_user.id)
        else:
            res = self.ctrl.create_maintenance(data, self.app.current_user.id)

        if res.success:
            messagebox.showinfo("OK", "Enregistré")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)


class FuelForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, veh_ctrl, emp_ctrl, cb) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.cb = cb

        vehs = veh_ctrl.get_all()
        self.veh_dict = {f"{v.immatriculation} - {v.marque}": v.id for v in vehs}

        emps = emp_ctrl.get_all()
        self.emp_dict = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in emps}

        self.title("Nouveau ravitaillement")
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        # champs
        ctk.CTkLabel(f, text="Véhicule *").grid(row=0, column=0, sticky='w', pady=8)
        self.veh = ctk.CTkComboBox(f, values=list(self.veh_dict.keys()), width=300)
        self.veh.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="Employé").grid(row=1, column=0, sticky='w', pady=8)
        self.emp = ctk.CTkComboBox(f, values=[''] + list(self.emp_dict.keys()), width=300)
        self.emp.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Date *").grid(row=2, column=0, sticky='w', pady=8)
        self.date = ctk.CTkEntry(f, width=300)
        self.date.insert(0, date.today().isoformat())
        self.date.grid(row=2, column=1, pady=8)

        ctk.CTkLabel(f, text="Quantité (L) *").grid(row=3, column=0, sticky='w', pady=8)
        self.litres = ctk.CTkEntry(f, width=300)
        self.litres.grid(row=3, column=1, pady=8)

        ctk.CTkLabel(f, text="Coût (€)").grid(row=4, column=0, sticky='w', pady=8)
        self.cout = ctk.CTkEntry(f, width=300)
        self.cout.grid(row=4, column=1, pady=8)

        ctk.CTkLabel(f, text="Station").grid(row=5, column=0, sticky='w', pady=8)
        self.station = ctk.CTkEntry(f, width=300)
        self.station.grid(row=5, column=1, pady=8)

        ctk.CTkLabel(f, text="Kilométrage").grid(row=6, column=0, sticky='w', pady=8)
        self.km = ctk.CTkEntry(f, width=300)
        self.km.grid(row=6, column=1, pady=8)

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

    def save(self) -> None:
        if not self.veh.get() or not self.date.get() or not self.litres.get():
            messagebox.showerror("Erreur", "Remplissez les champs obligatoires")
            return

        emp_key = self.emp.get()
        emp_id = self.emp_dict.get(emp_key) if emp_key else None

        data = {
            'vehicule_id': self.veh_dict[self.veh.get()],
            'employe_id': emp_id,
            'date': self.date.get(),
            'quantite_litres': self.litres.get(),
            'cout': self.cout.get() or None,
            'station': self.station.get() or None,
            'kilometrage': self.km.get() or None
        }

        res = self.ctrl.create_ravitaillement(data, self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Enregistré")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)