import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from controllers import MaintenanceController, VehicleController, EmployeeController, StatsController


class MaintenanceView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='white')
        self.app = app
        self.maint_ctrl = MaintenanceController()
        self.veh_ctrl = VehicleController()
        self.emp_ctrl = EmployeeController()
        self.stats_ctrl = StatsController()
        self.setup_maintenance()
        self.refresh()

    def setup_maintenance(self):
        # titre
        tk.Label(self, text="Maintenance & Carburant", font=('Arial', 18, 'bold'), bg='white').pack(pady=20)
        
        # onglets
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_maint_tab()
        self.create_fuel_tab()
        self.create_alert_tab()
    
    def create_maint_tab(self):
        tab = tk.Frame(self.tabs, bg='white')
        self.tabs.add(tab, text='Maintenance')

        # bouton ajouter
        tk.Button(tab, text="+ Intervention", command=self.add_maint, 
                 bg='green', fg='white').pack(anchor='e', padx=10, pady=10)
        
        # filtres
        flt = tk.Frame(tab, bg='white')
        flt.pack(fill='x', padx=10, pady=5)
        tk.Label(flt, text="Véhicule:", bg='white').pack(side='left')
        vehs = self.veh_ctrl.get_all()
        self.filter_veh = ttk.Combobox(flt, values=['Tous'] + [v.immatriculation for v in vehs], width=15)
        self.filter_veh.set('Tous')
        self.filter_veh.pack(side='left', padx=5)
        self.filter_veh.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        tk.Label(flt, text="Type:", bg='white').pack(side='left', padx=10)
        types = ['Vidange', 'Pneus', 'Freins', 'Réparation', 'Contrôle technique']
        self.filter_type = ttk.Combobox(flt, values=['Tous'] + types, width=15)
        self.filter_type.set('Tous')
        self.filter_type.pack(side='left', padx=5)
        self.filter_type.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # liste
        cols = ('date', 'vehicule', 'type', 'km', 'cout', 'prestataire')
        self.tree_maint = ttk.Treeview(tab, columns=cols, show='headings', height=12)
        self.tree_maint.heading('date', text='Date')
        self.tree_maint.heading('vehicule', text='Véhicule')
        self.tree_maint.heading('type', text='Type')
        self.tree_maint.heading('km', text='Km')
        self.tree_maint.heading('cout', text='Coût')
        self.tree_maint.heading('prestataire', text='Prestataire')
        self.tree_maint.pack(fill='both', expand=True, padx=10, pady=10)
        
        # boutons
        btns = tk.Frame(tab, bg='white')
        btns.pack(fill='x', padx=10, pady=10)
        tk.Button(btns, text="Modifier", command=self.edit_maint, bg='orange', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text="Supprimer", command=self.del_maint, bg='red', fg='white').pack(side='left', padx=5)
    
    def create_fuel_tab(self):
        tab = tk.Frame(self.tabs, bg='white')
        self.tabs.add(tab, text='Carburant')

        # bouton
        tk.Button(tab, text="+ Ravitaillement", command=self.add_fuel, 
                 bg='green', fg='white').pack(anchor='e', padx=10, pady=10)
        
        # filtre
        flt = tk.Frame(tab, bg='white')
        flt.pack(fill='x', padx=10, pady=5)
        tk.Label(flt, text="Véhicule:", bg='white').pack(side='left')
        vehs = self.veh_ctrl.get_all()
        self.filter_fuel = ttk.Combobox(flt, values=['Tous'] + [v.immatriculation for v in vehs], width=15)
        self.filter_fuel.set('Tous')
        self.filter_fuel.pack(side='left', padx=5)
        self.filter_fuel.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # liste
        cols = ('date', 'vehicule', 'employe', 'litres', 'cout', 'station')
        self.tree_fuel = ttk.Treeview(tab, columns=cols, show='headings', height=12)
        self.tree_fuel.heading('date', text='Date')
        self.tree_fuel.heading('vehicule', text='Véhicule')
        self.tree_fuel.heading('employe', text='Employé')
        self.tree_fuel.heading('litres', text='Litres')
        self.tree_fuel.heading('cout', text='Coût')
        self.tree_fuel.heading('station', text='Station')
        self.tree_fuel.pack(fill='both', expand=True, padx=10, pady=10)
        
        # boutons
        tk.Button(tab, text="Supprimer", command=self.del_fuel, bg='red', fg='white').pack(anchor='e', padx=10, pady=10)
    
    def create_alert_tab(self):
        tab = tk.Frame(self.tabs, bg='white')
        self.tabs.add(tab, text='Échéances')
        
        tk.Label(tab, text="Toutes les échéances à venir", font=('Arial', 10, 'italic'), 
                bg='white', fg='gray').pack(anchor='w', padx=10, pady=10)
        
        # liste
        cols = ('type', 'element', 'echeance', 'jours', 'statut')
        self.tree_alert = ttk.Treeview(tab, columns=cols, show='headings', height=15)
        self.tree_alert.heading('type', text='Type')
        self.tree_alert.heading('element', text='Élément')
        self.tree_alert.heading('echeance', text='Échéance')
        self.tree_alert.heading('jours', text='Jours')
        self.tree_alert.heading('statut', text='Statut')
        
        # couleurs
        self.tree_alert.tag_configure('ok', background='lightgreen')
        self.tree_alert.tag_configure('warning', background='yellow')
        self.tree_alert.tag_configure('expired', background='red')
        
        self.tree_alert.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh(self):
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

    def add_maint(self):
        MaintForm(self, self.app, self.maint_ctrl, self.veh_ctrl, None, self.refresh)

    def edit_maint(self):
        sel = self.tree_maint.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une intervention")
            return
        mid = int(self.tree_maint.item(sel[0], 'tags')[0])
        m = self.maint_ctrl.get_maintenance_by_id(mid)
        MaintForm(self, self.app, self.maint_ctrl, self.veh_ctrl, m, self.refresh)

    def del_maint(self):
        sel = self.tree_maint.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une intervention")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ?"):
            return
        mid = int(self.tree_maint.item(sel[0], 'tags')[0])
        self.maint_ctrl.delete_maintenance(mid, self.app.current_user.id)
        self.refresh()

    def add_fuel(self):
        FuelForm(self, self.app, self.maint_ctrl, self.veh_ctrl, self.emp_ctrl, self.refresh)

    def del_fuel(self):
        sel = self.tree_fuel.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un ravitaillement")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ?"):
            return
        rid = int(self.tree_fuel.item(sel[0], 'tags')[0])
        self.maint_ctrl.delete_ravitaillement(rid, self.app.current_user.id)
        self.refresh()


class MaintForm(tk.Toplevel):
    def __init__(self, parent, app, ctrl, veh_ctrl, maint, cb):
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.maint = maint
        self.cb = cb
        
        vehs = veh_ctrl.get_all()
        self.veh_dict = {f"{v.immatriculation} - {v.marque}": v.id for v in vehs}
        
        self.title("Modifier" if maint else "Nouvelle intervention")
        self.geometry("450x500")
        
        f = tk.Frame(self, bg='white', padx=20, pady=20)
        f.pack(fill='both', expand=True)
        
        # champs
        tk.Label(f, text="Véhicule *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.veh = ttk.Combobox(f, values=list(self.veh_dict.keys()), width=30)
        self.veh.grid(row=0, column=1, pady=5)
        
        tk.Label(f, text="Date *", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.date = tk.Entry(f, width=32)
        self.date.insert(0, date.today().isoformat())
        self.date.grid(row=1, column=1, pady=5)
        
        tk.Label(f, text="Type *", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        types = ['Vidange', 'Pneus', 'Freins', 'Réparation', 'Contrôle technique']
        self.type = ttk.Combobox(f, values=types, width=30)
        self.type.grid(row=2, column=1, pady=5)
        
        tk.Label(f, text="Kilométrage", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.km = tk.Entry(f, width=32)
        self.km.grid(row=3, column=1, pady=5)
        
        tk.Label(f, text="Coût (€)", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.cout = tk.Entry(f, width=32)
        self.cout.grid(row=4, column=1, pady=5)
        
        tk.Label(f, text="Prestataire", bg='white').grid(row=5, column=0, sticky='w', pady=5)
        self.prest = tk.Entry(f, width=32)
        self.prest.grid(row=5, column=1, pady=5)
        
        tk.Label(f, text="Remarques", bg='white').grid(row=6, column=0, sticky='nw', pady=5)
        self.rem = tk.Text(f, width=30, height=3)
        self.rem.grid(row=6, column=1, pady=5)
        
        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', pady=10)
        tk.Button(btns, text="Enregistrer", command=self.save, bg='green', fg='white', width=12).pack(side='right', padx=20)
        tk.Button(btns, text="Annuler", command=self.destroy, bg='gray', fg='white', width=12).pack(side='right', padx=5)
        
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
    
    def save(self):
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


class FuelForm(tk.Toplevel):
    def __init__(self, parent, app, ctrl, veh_ctrl, emp_ctrl, cb):
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.cb = cb
        
        vehs = veh_ctrl.get_all()
        self.veh_dict = {f"{v.immatriculation} - {v.marque}": v.id for v in vehs}
        
        emps = emp_ctrl.get_all()
        self.emp_dict = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in emps}
        
        self.title("Nouveau ravitaillement")
        self.geometry("450x400")
        
        f = tk.Frame(self, bg='white', padx=20, pady=20)
        f.pack(fill='both', expand=True)
        
        # champs
        tk.Label(f, text="Véhicule *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.veh = ttk.Combobox(f, values=list(self.veh_dict.keys()), width=30)
        self.veh.grid(row=0, column=1, pady=5)
        
        tk.Label(f, text="Employé", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.emp = ttk.Combobox(f, values=[''] + list(self.emp_dict.keys()), width=30)
        self.emp.grid(row=1, column=1, pady=5)
        
        tk.Label(f, text="Date *", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.date = tk.Entry(f, width=32)
        self.date.insert(0, date.today().isoformat())
        self.date.grid(row=2, column=1, pady=5)
        
        tk.Label(f, text="Quantité (L) *", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.litres = tk.Entry(f, width=32)
        self.litres.grid(row=3, column=1, pady=5)
        
        tk.Label(f, text="Coût (€)", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.cout = tk.Entry(f, width=32)
        self.cout.grid(row=4, column=1, pady=5)
        
        tk.Label(f, text="Station", bg='white').grid(row=5, column=0, sticky='w', pady=5)
        self.station = tk.Entry(f, width=32)
        self.station.grid(row=5, column=1, pady=5)
        
        tk.Label(f, text="Kilométrage", bg='white').grid(row=6, column=0, sticky='w', pady=5)
        self.km = tk.Entry(f, width=32)
        self.km.grid(row=6, column=1, pady=5)
        
        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', pady=10)
        tk.Button(btns, text="Enregistrer", command=self.save, bg='green', fg='white', width=12).pack(side='right', padx=20)
        tk.Button(btns, text="Annuler", command=self.destroy, bg='gray', fg='white', width=12).pack(side='right', padx=5)
    
    def save(self):
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