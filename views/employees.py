# views/employees.py - Vue de gestion des employés (MVC)
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable
from datetime import datetime, date

from controllers import EmployeeController
from widgets import FilterableTreeview, BaseFormDialog, SearchBar, AlertBanner
from config import SERVICES


class EmployeesView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = EmployeeController()
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(header, text="Gestion des employés", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')

        if self.app.current_user.role in ('admin', 'gestionnaire'):
            tk.Button(header, text="Nouvel employé", command=lambda: self._show_form(),
                     bg='#27ae60', fg='#000000', relief='flat').pack(side='right')

        self.search_bar = SearchBar(self, on_search=self.refresh, filters=[("Service", "service", SERVICES)])
        self.search_bar.pack(fill='x', padx=20, pady=10)

        self.authorized_only = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Afficher uniquement les autorisés", variable=self.authorized_only,
                      bg='#ffffff', fg='#000000', command=self.refresh).pack(anchor='w', padx=20)

        self.alert_banner = AlertBanner(self, "Certains permis arrivent à expiration !")
        
        columns = [('matricule', 'Matricule', 100), ('nom', 'Nom', 120), ('prenom', 'Prénom', 120),
                   ('service', 'Service', 120), ('telephone', 'Téléphone', 120), ('permis', 'N° Permis', 120),
                   ('validite', 'Validité', 100), ('autorise', 'Autorisé', 80)]
        self.tree = FilterableTreeview(self, columns=columns, on_double_click=self._show_detail, on_right_click=self._show_menu)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.tree.configure_tag('permis_ok', background='#d5f4e6')
        self.tree.configure_tag('permis_warning', background='#ffeaa7')
        self.tree.configure_tag('permis_expired', background='#fab1a0')
        
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Voir fiche", command=self._show_detail)
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            self.context_menu.add_command(label="Modifier", command=self._edit_selected)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Supprimer", command=self._delete_selected)
    
    def _show_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    
    def _get_permis_tag(self, date_validite):
        if not date_validite:
            return 'permis_ok'
        try:
            validity = datetime.strptime(date_validite, '%Y-%m-%d').date()
            days = (validity - date.today()).days
            return 'permis_expired' if days < 0 else 'permis_warning' if days < 30 else 'permis_ok'
        except:
            return 'permis_ok'
    
    def refresh(self):
        filters = {}
        search = self.search_bar.get_value('search')
        if search:
            filters['search'] = search
        service = self.search_bar.get_value('service')
        if service:
            filters['service'] = service
        if self.authorized_only.get():
            filters['autorise_only'] = True
        
        employees = self.controller.get_all(filters if filters else None)
        self.tree.clear()
        has_expiring = False
        
        for e in employees:
            tag = self._get_permis_tag(e.date_validite_permis)
            if tag in ('permis_warning', 'permis_expired'):
                has_expiring = True
            self.tree.insert(values=(e.matricule, e.nom, e.prenom, e.service or '-', e.telephone or '-',
                e.num_permis or '-', e.date_validite_permis or '-', 'Oui' if e.autorise_conduire else 'Non'),
                tags=(tag, str(e.id)))
        
        self.alert_banner.show() if has_expiring else self.alert_banner.hide()
    
    def _get_selected_id(self):
        eid = self.tree.get_selected_id(tag_index=1)
        if eid is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un employé")
        return eid
    
    def _show_form(self, employee=None):
        EmployeeFormDialog(self, self.app, self.controller, employee, self.refresh)
    
    def _edit_selected(self):
        eid = self._get_selected_id()
        if eid:
            self._show_form(self.controller.get_by_id(eid))
    
    def _delete_selected(self):
        eid = self._get_selected_id()
        if not eid:
            return
        emp = self.controller.get_by_id(eid)
        if emp and messagebox.askyesno("Confirmation", f"Supprimer {emp.full_name} ?"):
            result = self.controller.delete(eid, self.app.current_user.id)
            if result.success:
                self.refresh()
    
    def _show_detail(self):
        eid = self._get_selected_id()
        if eid:
            EmployeeDetailDialog(self, self.app, self.controller, eid)


class EmployeeFormDialog(BaseFormDialog):
    def __init__(self, parent, app, controller, employee=None, refresh_callback=None):
        self.app = app
        self.controller = controller
        self.employee = employee
        self.refresh_callback = refresh_callback
        super().__init__(parent, "Modifier l'employé" if employee else "Nouvel employé", width=500, height=550)
        self._build_form()
        if employee:
            self._load_data()
    
    def _build_form(self):
        self.add_section_title("Informations personnelles")
        self.add_entry("Matricule *", "matricule")
        self.add_entry("Nom *", "nom")
        self.add_entry("Prénom *", "prenom")
        self.add_combobox("Service", "service", SERVICES)
        self.add_entry("Téléphone", "telephone")
        self.add_entry("Email", "email")
        self.add_section_title("Permis de conduire")
        self.add_entry("N° Permis", "num_permis")
        self.add_entry("Date validité (AAAA-MM-JJ)", "date_validite_permis")
        self.add_checkbox("Autorisé à conduire", "autorise_conduire")
        self.add_file_picker("Photo", "photo_path", [("Images", "*.png *.jpg *.jpeg")])
        self.add_buttons(on_save=self._save)
    
    def _load_data(self):
        if self.employee:
            for key in self.vars:
                value = getattr(self.employee, key, None)
                if value is not None:
                    self.set_value(key, value)
    
    def _save(self):
        data = {key: self.get_value(key) for key in self.vars}
        if self.employee:
            result = self.controller.update(self.employee.id, data, self.app.current_user.id)
        else:
            result = self.controller.create(data, self.app.current_user.id)
        
        if result.success:
            self.show_success(result.message)
            if self.refresh_callback:
                self.refresh_callback()
            self.destroy()
        else:
            self.show_error(result.message)


class EmployeeDetailDialog(tk.Toplevel):
    def __init__(self, parent, app, controller, employee_id):
        super().__init__(parent)
        self.app = app
        self.controller = controller
        self.employee = controller.get_by_id(employee_id)

        self.title(f"Fiche - {self.employee.full_name}")
        self.geometry("700x500")
        self.configure(bg='#ffffff')
        self.transient(parent)
        self._create_widgets()

    def _create_widgets(self):
        e = self.employee
        header = tk.Frame(self, bg='#f5f5f5', pady=15)
        header.pack(fill='x')
        tk.Label(header, text=f"{e.full_name}", font=('Helvetica', 18, 'bold'), bg='#f5f5f5', fg='#000000').pack(side='left', padx=20)
        tk.Label(header, text=f"({e.matricule})", font=('Helvetica', 14), bg='#f5f5f5', fg='#333333').pack(side='left')

        auth_color = '#27ae60' if e.autorise_conduire else '#e74c3c'
        tk.Label(header, text='Autorisé' if e.autorise_conduire else 'Non autorisé',
                font=('Helvetica', 10, 'bold'), bg=auth_color, fg='#000000', padx=10, pady=3).pack(side='right', padx=20)
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Info tab
        frame = tk.Frame(notebook, bg='white')
        notebook.add(frame, text='Informations')
        grid = tk.Frame(frame, bg='white')
        grid.pack(fill='both', expand=True, padx=20, pady=20)
        infos = [("Matricule", e.matricule), ("Nom", e.nom), ("Prénom", e.prenom), ("Service", e.service or '-'),
                 ("Téléphone", e.telephone or '-'), ("Email", e.email or '-'), ("N° Permis", e.num_permis or '-'),
                 ("Validité", e.date_validite_permis or '-')]
        for i, (label, value) in enumerate(infos):
            r, c = i // 2, (i % 2) * 2
            tk.Label(grid, text=f"{label}:", font=('Helvetica', 10, 'bold'), bg='white', fg='#666666').grid(row=r, column=c, sticky='e', padx=(20, 5), pady=5)
            tk.Label(grid, text=str(value), font=('Helvetica', 10), bg='white', fg='#000000').grid(row=r, column=c+1, sticky='w', pady=5)

        # Sorties tab
        frame2 = tk.Frame(notebook, bg='white')
        notebook.add(frame2, text='Historique sorties')
        cols = [('date', 'Date', 100), ('vehicule', 'Véhicule', 150), ('motif', 'Motif', 150), ('dest', 'Destination', 120), ('km', 'Km', 80)]
        tree = FilterableTreeview(frame2, columns=cols)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        for s in self.controller.get_sorties(self.employee.id):
            km = (s['km_retour'] - s['km_depart']) if s['km_retour'] and s['km_depart'] else '-'
            tree.insert(values=(s['date_sortie_reelle'] or '-', f"{s['immatriculation']} ({s['marque']})",
                s['motif'] or '-', s['destination'] or '-', f"{km} km" if isinstance(km, int) else km))
