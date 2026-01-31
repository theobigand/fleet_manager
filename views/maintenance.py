# views/maintenance.py - Maintenance et carburant (MVC)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from controllers import MaintenanceController, VehicleController, EmployeeController, StatsController
from widgets import FilterableTreeview, BaseFormDialog
from config import MAINTENANCE_TYPES


class MaintenanceView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = MaintenanceController()
        self.vehicle_ctrl = VehicleController()
        self.employee_ctrl = EmployeeController()
        self.stats_ctrl = StatsController()
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(header, text="Maintenance & Carburant", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        self._create_maintenance_tab()
        self._create_carburant_tab()
        self._create_echeances_tab()
    
    def _create_maintenance_tab(self):
        frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(frame, text='Maintenance')

        h = tk.Frame(frame, bg='white')
        h.pack(fill='x', padx=10, pady=10)
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            tk.Button(h, text="Nouvelle intervention", command=self._add_maintenance, bg='#27ae60', fg='#000000', relief='flat').pack(side='right')
        
        flt = tk.Frame(frame, bg='white')
        flt.pack(fill='x', padx=10, pady=5)
        tk.Label(flt, text="Véhicule:", bg='white').pack(side='left')
        vehicles = self.vehicle_ctrl.get_all()
        self.maint_veh_filter = ttk.Combobox(flt, values=[''] + [v.immatriculation for v in vehicles], state='readonly', width=15)
        self.maint_veh_filter.pack(side='left', padx=5)
        self.maint_veh_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        tk.Label(flt, text="Type:", bg='white').pack(side='left', padx=(15, 0))
        self.maint_type_filter = ttk.Combobox(flt, values=[''] + MAINTENANCE_TYPES, state='readonly', width=15)
        self.maint_type_filter.pack(side='left', padx=5)
        self.maint_type_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        cols = [('date', 'Date', 100), ('vehicule', 'Véhicule', 130), ('type', 'Type', 130),
                ('km', 'Km', 100), ('cout', 'Coût', 100), ('prest', 'Prestataire', 120), ('prochaine', 'Prochaine', 120)]
        self.tree_maint = FilterableTreeview(frame, columns=cols, on_right_click=self._maint_menu)
        self.tree_maint.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.maint_ctx = tk.Menu(self, tearoff=0)
        self.maint_ctx.add_command(label="Modifier", command=self._edit_maintenance)
        self.maint_ctx.add_command(label="Supprimer", command=self._del_maintenance)
    
    def _create_carburant_tab(self):
        frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(frame, text='Carburant')

        h = tk.Frame(frame, bg='white')
        h.pack(fill='x', padx=10, pady=10)
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            tk.Button(h, text="Nouveau ravitaillement", command=self._add_ravitaillement, bg='#27ae60', fg='#000000', relief='flat').pack(side='right')
        
        flt = tk.Frame(frame, bg='white')
        flt.pack(fill='x', padx=10, pady=5)
        tk.Label(flt, text="Véhicule:", bg='white').pack(side='left')
        vehicles = self.vehicle_ctrl.get_all()
        self.fuel_veh_filter = ttk.Combobox(flt, values=[''] + [v.immatriculation for v in vehicles], state='readonly', width=15)
        self.fuel_veh_filter.pack(side='left', padx=5)
        self.fuel_veh_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        cols = [('date', 'Date', 100), ('vehicule', 'Véhicule', 130), ('employe', 'Employé', 130),
                ('litres', 'Litres', 80), ('cout', 'Coût', 100), ('station', 'Station', 120), ('km', 'Km', 100)]
        self.tree_fuel = FilterableTreeview(frame, columns=cols, on_right_click=self._fuel_menu)
        self.tree_fuel.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.fuel_ctx = tk.Menu(self, tearoff=0)
        self.fuel_ctx.add_command(label="Supprimer", command=self._del_ravitaillement)
    
    def _create_echeances_tab(self):
        frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(frame, text='Échéances')
        tk.Label(frame, text="Tableau centralisé des échéances", font=('Helvetica', 10, 'italic'), bg='white', fg='#666666').pack(anchor='w', padx=10, pady=10)
        cols = [('type', 'Type', 150), ('element', 'Élément', 180), ('echeance', 'Échéance', 120), ('jours', 'Jours', 100), ('statut', 'Statut', 100)]
        self.tree_ech = FilterableTreeview(frame, columns=cols)
        self.tree_ech.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree_ech.configure_tag('ok', background='#d5f4e6')
        self.tree_ech.configure_tag('warning', background='#ffeaa7')
        self.tree_ech.configure_tag('expired', background='#fab1a0')
    
    def _maint_menu(self, event):
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            self.maint_ctx.post(event.x_root, event.y_root)
    
    def _fuel_menu(self, event):
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            self.fuel_ctx.post(event.x_root, event.y_root)
    
    def refresh(self):
        veh = self.maint_veh_filter.get() if hasattr(self, 'maint_veh_filter') else ''
        typ = self.maint_type_filter.get() if hasattr(self, 'maint_type_filter') else ''
        self.tree_maint.clear()
        for m in self.controller.get_all_maintenances(veh or None, typ or None):
            self.tree_maint.insert(values=(m.date, f"{m.immatriculation} ({m.marque})", m.type_intervention,
                f"{m.kilometrage:,}".replace(',', ' ') if m.kilometrage else '-', f"{m.cout:.2f} €" if m.cout else '-',
                m.prestataire or '-', m.date_prochaine_echeance or '-'), tags=('maint', str(m.id)))

        veh2 = self.fuel_veh_filter.get() if hasattr(self, 'fuel_veh_filter') else ''
        self.tree_fuel.clear()
        for r in self.controller.get_all_ravitaillements(veh2 or None):
            emp = f"{r.prenom} {r.nom}" if r.prenom else '-'
            self.tree_fuel.insert(values=(r.date, f"{r.immatriculation} ({r.marque})", emp, f"{r.quantite_litres:.1f} L",
                f"{r.cout:.2f} €" if r.cout else '-', r.station or '-', f"{r.kilometrage:,}".replace(',', ' ') if r.kilometrage else '-'),
                tags=('fuel', str(r.id)))

        self.tree_ech.clear()
        for e in self.stats_ctrl.get_all_echeances():
            days = e.get('jours_restants')
            tag = 'expired' if days is not None and days < 0 else 'warning' if days is not None and days < 30 else 'ok'
            statut = 'DÉPASSÉ' if days is not None and days < 0 else f'{days} jours' if days is not None else '-'
            self.tree_ech.insert(values=(e['type'], e['element'], e['date_echeance'] or '-', days if days is not None else '-', statut), tags=(tag,))
    
    def _add_maintenance(self):
        MaintenanceFormDialog(self, self.app, self.controller, self.vehicle_ctrl, None, self.refresh)
    
    def _edit_maintenance(self):
        mid = self.tree_maint.get_selected_id(tag_index=1)
        if mid:
            MaintenanceFormDialog(self, self.app, self.controller, self.vehicle_ctrl, self.controller.get_maintenance_by_id(mid), self.refresh)
    
    def _del_maintenance(self):
        mid = self.tree_maint.get_selected_id(tag_index=1)
        if mid and messagebox.askyesno("Confirmation", "Supprimer cette intervention ?"):
            self.controller.delete_maintenance(mid, self.app.current_user.id)
            self.refresh()
    
    def _add_ravitaillement(self):
        RavitaillementFormDialog(self, self.app, self.controller, self.vehicle_ctrl, self.employee_ctrl, self.refresh)
    
    def _del_ravitaillement(self):
        rid = self.tree_fuel.get_selected_id(tag_index=1)
        if rid and messagebox.askyesno("Confirmation", "Supprimer ce ravitaillement ?"):
            self.controller.delete_ravitaillement(rid, self.app.current_user.id)
            self.refresh()


class MaintenanceFormDialog(BaseFormDialog):
    def __init__(self, parent, app, controller, vehicle_ctrl, maint, refresh_cb):
        self.app = app
        self.controller = controller
        self.maint = maint
        self.refresh_cb = refresh_cb
        
        vehicles = vehicle_ctrl.get_all()
        self.vehicle_choices = [f"{v.immatriculation} - {v.marque} {v.modele}" for v in vehicles]
        self.vehicle_ids = {f"{v.immatriculation} - {v.marque} {v.modele}": v.id for v in vehicles}
        
        super().__init__(parent, "Modifier" if maint else "Nouvelle intervention", width=500, height=500)
        self._build_form()
        if maint:
            self._load_data()
    
    def _build_form(self):
        self.add_section_title("Intervention")
        self.add_combobox("Véhicule *", "vehicule", self.vehicle_choices)
        self.add_entry("Date (AAAA-MM-JJ) *", "date", default=date.today().isoformat())
        self.add_combobox("Type *", "type_intervention", MAINTENANCE_TYPES)
        self.add_entry("Kilométrage", "kilometrage")
        self.add_entry("Coût (€)", "cout")
        self.add_entry("Prestataire", "prestataire")
        self.add_text("Remarques", "remarques", height=3)
        self.add_entry("Prochaine échéance", "date_prochaine_echeance")
        self.add_buttons(on_save=self._save)
    
    def _load_data(self):
        for c, vid in self.vehicle_ids.items():
            if vid == self.maint.vehicule_id:
                self.set_value('vehicule', c)
                break
        self.set_value('date', self.maint.date or '')
        self.set_value('type_intervention', self.maint.type_intervention or '')
        self.set_value('kilometrage', self.maint.kilometrage or '')
        self.set_value('cout', self.maint.cout or '')
        self.set_value('prestataire', self.maint.prestataire or '')
        self.set_value('remarques', self.maint.remarques or '')
        self.set_value('date_prochaine_echeance', self.maint.date_prochaine_echeance or '')
    
    def _save(self):
        data = {'vehicule_id': self.vehicle_ids.get(self.get_value('vehicule')),
                'date': self.get_value('date'), 'type_intervention': self.get_value('type_intervention'),
                'kilometrage': self.get_value('kilometrage'), 'cout': self.get_value('cout'),
                'prestataire': self.get_value('prestataire'), 'remarques': self.get_value('remarques'),
                'date_prochaine_echeance': self.get_value('date_prochaine_echeance')}
        if self.maint:
            result = self.controller.update_maintenance(self.maint.id, data, self.app.current_user.id)
        else:
            result = self.controller.create_maintenance(data, self.app.current_user.id)
        if result.success:
            self.show_success(result.message)
            if self.refresh_cb:
                self.refresh_cb()
            self.destroy()
        else:
            self.show_error(result.message)


class RavitaillementFormDialog(BaseFormDialog):
    def __init__(self, parent, app, controller, vehicle_ctrl, employee_ctrl, refresh_cb):
        self.app = app
        self.controller = controller
        self.refresh_cb = refresh_cb
        
        vehicles = vehicle_ctrl.get_all()
        self.vehicle_choices = [f"{v.immatriculation} - {v.marque}" for v in vehicles]
        self.vehicle_ids = {f"{v.immatriculation} - {v.marque}": v.id for v in vehicles}
        
        employees = employee_ctrl.get_all()
        self.employee_choices = [''] + [f"{e.matricule} - {e.full_name}" for e in employees]
        self.employee_ids = {f"{e.matricule} - {e.full_name}": e.id for e in employees}
        
        super().__init__(parent, "Nouveau ravitaillement", width=500, height=450)
        self._build_form()
    
    def _build_form(self):
        self.add_section_title("Ravitaillement")
        self.add_combobox("Véhicule *", "vehicule", self.vehicle_choices)
        self.add_combobox("Employé", "employe", self.employee_choices)
        self.add_entry("Date (AAAA-MM-JJ) *", "date", default=date.today().isoformat())
        self.add_entry("Quantité (L) *", "quantite_litres")
        self.add_entry("Coût (€)", "cout")
        self.add_entry("Station", "station")
        self.add_entry("Kilométrage", "kilometrage")
        self.add_buttons(on_save=self._save)
    
    def _save(self):
        data = {'vehicule_id': self.vehicle_ids.get(self.get_value('vehicule')),
                'employe_id': self.employee_ids.get(self.get_value('employe')),
                'date': self.get_value('date'), 'quantite_litres': self.get_value('quantite_litres'),
                'cout': self.get_value('cout'), 'station': self.get_value('station'), 'kilometrage': self.get_value('kilometrage')}
        result = self.controller.create_ravitaillement(data, self.app.current_user.id)
        if result.success:
            self.show_success(result.message)
            if self.refresh_cb:
                self.refresh_cb()
            self.destroy()
        else:
            self.show_error(result.message)
