# views/vehicles.py - Vue de gestion des véhicules (MVC)
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable

from controllers import VehicleController
from widgets import FilterableTreeview, BaseFormDialog, SearchBar, AlertBanner
from config import (VEHICLE_TYPES, FUEL_TYPES, SERVICES, VEHICLE_STATUSES, 
                    AFFECTATION_TYPES, COLORS, DEFAULT_REVISION_KM)


class VehiclesView(tk.Frame):
    """Vue de gestion des véhicules - Affichage uniquement"""

    def __init__(self, parent: tk.Widget, app: Any):
        super().__init__(parent)
        self.app = app
        self.controller = VehicleController()
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()

    def _create_widgets(self) -> None:
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))

        tk.Label(header, text="Gestion des véhicules",
                font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')

        if self.app.current_user.role in ('admin', 'gestionnaire'):
            tk.Button(header, text="Nouveau véhicule", command=lambda: self._show_form(),
                     bg='#27ae60', fg='#000000', relief='flat', cursor='hand2').pack(side='right')

        self.search_bar = SearchBar(self, on_search=self.refresh, filters=[
            ("Statut", "statut", list(VEHICLE_STATUSES.keys())),
            ("Type", "type_vehicule", VEHICLE_TYPES),
            ("Affectation", "type_affectation", list(AFFECTATION_TYPES.keys())),
        ])
        self.search_bar.pack(fill='x', padx=20, pady=10)

        self.alert_banner = AlertBanner(self, "PARC COMPLET - Aucun véhicule disponible")
        
        columns = [
            ('immat', 'Immatriculation', 120), ('marque', 'Marque', 100),
            ('modele', 'Modèle', 100), ('type', 'Type', 90), ('statut', 'Statut', 100),
            ('km', 'Kilométrage', 100), ('affectation', 'Affectation', 100), ('service', 'Service', 100),
        ]
        self.tree = FilterableTreeview(self, columns=columns,
            on_double_click=self._show_detail, on_right_click=self._show_context_menu)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        
        for status, color in COLORS.items():
            self.tree.configure_tag(status, background=color)
        
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Voir détails", command=self._show_detail)
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            self.context_menu.add_command(label="Modifier", command=self._edit_selected)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Supprimer", command=self._delete_selected)
    
    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.post(event.x_root, event.y_root)
    
    def refresh(self) -> None:
        filters: Dict[str, Any] = {}
        search = self.search_bar.get_value('search')
        if search:
            filters['search'] = search
        for key in ('statut', 'type_vehicule', 'type_affectation'):
            value = self.search_bar.get_value(key)
            if value:
                filters[key] = value
        
        vehicles = self.controller.get_all(filters if filters else None)
        self.tree.clear()
        available_count = 0
        
        for v in vehicles:
            if v.is_available:
                available_count += 1
            self.tree.insert(
                values=(v.immatriculation, v.marque, v.modele, v.type_vehicule or '-',
                    VEHICLE_STATUSES.get(v.statut, v.statut), v.formatted_km,
                    AFFECTATION_TYPES.get(v.type_affectation, v.type_affectation), v.service_principal or '-'),
                tags=(v.statut, str(v.id))
            )
        
        if available_count == 0 and len(vehicles) > 0:
            self.alert_banner.show()
        else:
            self.alert_banner.hide()
    
    def _get_selected_vehicle_id(self) -> Optional[int]:
        vehicle_id = self.tree.get_selected_id(tag_index=1)
        if vehicle_id is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule")
        return vehicle_id
    
    def _show_form(self, vehicle=None) -> None:
        VehicleFormDialog(self, self.app, self.controller, vehicle, self.refresh)
    
    def _edit_selected(self) -> None:
        vehicle_id = self._get_selected_vehicle_id()
        if vehicle_id:
            self._show_form(self.controller.get_by_id(vehicle_id))
    
    def _delete_selected(self) -> None:
        vehicle_id = self._get_selected_vehicle_id()
        if not vehicle_id:
            return
        vehicle = self.controller.get_by_id(vehicle_id)
        if vehicle and messagebox.askyesno("Confirmation", f"Supprimer {vehicle.immatriculation} ?"):
            result = self.controller.delete(vehicle_id, self.app.current_user.id)
            if result.success:
                self.refresh()
            else:
                messagebox.showerror("Erreur", result.message)
    
    def _show_detail(self) -> None:
        vehicle_id = self._get_selected_vehicle_id()
        if vehicle_id:
            VehicleDetailDialog(self, self.app, self.controller, vehicle_id)


class VehicleFormDialog(BaseFormDialog):
    """Formulaire véhicule - Appelle le controller pour la logique"""
    
    def __init__(self, parent, app, controller: VehicleController, vehicle=None, refresh_callback=None):
        self.app = app
        self.controller = controller
        self.vehicle = vehicle
        self.refresh_callback = refresh_callback
        title = "Modifier le véhicule" if vehicle else "Nouveau véhicule"
        super().__init__(parent, title, width=600, height=650)
        self._build_form()
        if vehicle:
            self._load_data()
    
    def _build_form(self) -> None:
        self.add_section_title("Informations générales")
        self.add_entry("Immatriculation *", "immatriculation")
        self.add_entry("Marque *", "marque")
        self.add_entry("Modèle *", "modele")
        self.add_combobox("Type de véhicule", "type_vehicule", VEHICLE_TYPES)
        self.add_entry("Année", "annee")
        self.add_entry("Date acquisition (AAAA-MM-JJ)", "date_acquisition")
        self.add_entry("Kilométrage actuel", "kilometrage_actuel", default="0")
        self.add_combobox("Carburant", "carburant", FUEL_TYPES)
        self.add_entry("Puissance fiscale (CV)", "puissance_fiscale")
        self.add_entry("N° châssis", "numero_chassis")
        
        self.add_section_title("Affectation")
        self.add_combobox("Service principal", "service_principal", SERVICES)
        self.add_combobox("Type affectation", "type_affectation", list(AFFECTATION_TYPES.keys()), default="mutualise")
        self.add_combobox("Statut", "statut", list(VEHICLE_STATUSES.keys()), default="disponible")
        self.add_entry("Seuil révision (km)", "seuil_revision_km", default=str(DEFAULT_REVISION_KM))
        self.add_file_picker("Photo", "photo_path", [("Images", "*.png *.jpg *.jpeg")])
        self.add_buttons(on_save=self._save)
    
    def _load_data(self) -> None:
        if self.vehicle:
            for key in self.vars:
                value = getattr(self.vehicle, key, None)
                if value is not None:
                    self.set_value(key, value)
    
    def _save(self) -> None:
        # La vue collecte les données, le controller valide et persiste
        data = {key: self.get_value(key) for key in self.vars}
        
        if self.vehicle:
            result = self.controller.update(self.vehicle.id, data, self.app.current_user.id)
        else:
            result = self.controller.create(data, self.app.current_user.id)
        
        if result.success:
            self.show_success(result.message)
            if self.refresh_callback:
                self.refresh_callback()
            self.destroy()
        else:
            self.show_error(result.message)


class VehicleDetailDialog(tk.Toplevel):
    """Fiche détaillée véhicule"""

    def __init__(self, parent, app, controller: VehicleController, vehicle_id: int):
        super().__init__(parent)
        self.app = app
        self.controller = controller
        self.vehicle_id = vehicle_id
        self.vehicle = controller.get_by_id(vehicle_id)

        self.title(f"Fiche - {self.vehicle.immatriculation}")
        self.geometry("800x600")
        self.configure(bg='#ffffff')
        self.transient(parent)
        self._create_widgets()

    def _create_widgets(self) -> None:
        v = self.vehicle

        header = tk.Frame(self, bg='#f5f5f5', pady=15)
        header.pack(fill='x')
        tk.Label(header, text=f"{v.immatriculation}", font=('Helvetica', 18, 'bold'),
                bg='#f5f5f5', fg='#000000').pack(side='left', padx=20)
        tk.Label(header, text=f"{v.marque} {v.modele}",
                font=('Helvetica', 14), bg='#f5f5f5', fg='#333333').pack(side='left')

        status_color = COLORS.get(v.statut, '#95a5a6')
        tk.Label(header, text=VEHICLE_STATUSES.get(v.statut, v.statut),
                font=('Helvetica', 10, 'bold'), bg=status_color, padx=10, pady=3).pack(side='right', padx=20)
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self._create_info_tab(notebook)
        self._create_sorties_tab(notebook)
        self._create_maintenance_tab(notebook)
        self._create_documents_tab(notebook)
        self._create_fuel_tab(notebook)
    
    def _create_info_tab(self, notebook) -> None:
        frame = tk.Frame(notebook, bg='white')
        notebook.add(frame, text='Informations')
        grid = tk.Frame(frame, bg='white')
        grid.pack(fill='both', expand=True, padx=20, pady=20)

        v = self.vehicle
        infos = [
            ("Immatriculation", v.immatriculation), ("Marque", v.marque), ("Modèle", v.modele),
            ("Type", v.type_vehicule or '-'), ("Année", v.annee or '-'), ("Acquisition", v.date_acquisition or '-'),
            ("Kilométrage", v.formatted_km), ("Carburant", v.carburant or '-'),
            ("Puissance", f"{v.puissance_fiscale} CV" if v.puissance_fiscale else '-'),
            ("Châssis", v.numero_chassis or '-'), ("Service", v.service_principal or '-'),
            ("Affectation", AFFECTATION_TYPES.get(v.type_affectation, '-')),
        ]

        for i, (label, value) in enumerate(infos):
            r, c = i // 2, (i % 2) * 2
            tk.Label(grid, text=f"{label}:", font=('Helvetica', 10, 'bold'),
                    bg='white', fg='#666666').grid(row=r, column=c, sticky='e', padx=(20, 5), pady=5)
            tk.Label(grid, text=str(value), font=('Helvetica', 10),
                    bg='white', fg='#000000').grid(row=r, column=c+1, sticky='w', pady=5)
    
    def _create_sorties_tab(self, notebook) -> None:
        frame = tk.Frame(notebook, bg='white')
        notebook.add(frame, text='Sorties')
        cols = [('date', 'Date', 100), ('employe', 'Employé', 150), ('motif', 'Motif', 150),
                ('dest', 'Destination', 120), ('km', 'Km', 80), ('statut', 'Statut', 80)]
        tree = FilterableTreeview(frame, columns=cols)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        for s in self.controller.get_sorties(self.vehicle_id):
            km = (s['km_retour'] - s['km_depart']) if s['km_retour'] and s['km_depart'] else '-'
            tree.insert(values=(s['date_sortie_reelle'] or s['date_sortie_prevue'], f"{s['prenom']} {s['nom']}",
                s['motif'] or '-', s['destination'] or '-', f"{km} km" if isinstance(km, int) else km, s['statut']))
    
    def _create_maintenance_tab(self, notebook) -> None:
        frame = tk.Frame(notebook, bg='white')
        notebook.add(frame, text='Maintenance')
        cols = [('date', 'Date', 100), ('type', 'Type', 150), ('km', 'Km', 100), ('cout', 'Coût', 100), ('prest', 'Prestataire', 120)]
        tree = FilterableTreeview(frame, columns=cols)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        for m in self.controller.get_maintenances(self.vehicle_id):
            tree.insert(values=(m['date'], m['type_intervention'],
                f"{m['kilometrage']:,}".replace(',', ' ') if m['kilometrage'] else '-',
                f"{m['cout']:.2f} €" if m['cout'] else '-', m['prestataire'] or '-'))
    
    def _create_documents_tab(self, notebook) -> None:
        frame = tk.Frame(notebook, bg='white')
        notebook.add(frame, text='Documents')
        cols = [('type', 'Type', 150), ('emission', 'Émission', 100), ('echeance', 'Échéance', 100), ('desc', 'Description', 200)]
        tree = FilterableTreeview(frame, columns=cols)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        for d in self.controller.get_documents(self.vehicle_id):
            tree.insert(values=(d['type_document'], d['date_emission'] or '-', d['date_echeance'] or '-', d['description'] or '-'))
    
    def _create_fuel_tab(self, notebook) -> None:
        frame = tk.Frame(notebook, bg='white')
        notebook.add(frame, text='Carburant')
        conso = self.controller.calculate_consumption(self.vehicle_id)
        h = tk.Frame(frame, bg='white')
        h.pack(fill='x', padx=10, pady=10)
        tk.Label(h, text="Conso moyenne:", font=('Helvetica', 10, 'bold'), bg='white', fg='#000000').pack(side='left')
        tk.Label(h, text=f"{conso} L/100km" if conso else "N/A", font=('Helvetica', 10), bg='white',
                fg='#5cb85c' if conso else '#666666').pack(side='left', padx=5)
        cols = [('date', 'Date', 100), ('emp', 'Employé', 150), ('l', 'Litres', 80), ('c', 'Coût', 80), ('st', 'Station', 120)]
        tree = FilterableTreeview(frame, columns=cols)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        for r in self.controller.get_ravitaillements(self.vehicle_id):
            tree.insert(values=(r['date'], f"{r['prenom']} {r['nom']}" if r.get('prenom') else '-',
                f"{r['quantite_litres']:.1f} L", f"{r['cout']:.2f} €" if r['cout'] else '-', r['station'] or '-'))
