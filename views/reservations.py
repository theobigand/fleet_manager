# views/reservations.py - Réservations et sorties (MVC)
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import datetime, date

from controllers import SortieController, VehicleController, EmployeeController
from widgets import FilterableTreeview, BaseFormDialog
from config import FUEL_LEVELS, RETURN_STATES


class ReservationsView(tk.Frame):
    def __init__(self, parent, app, preselect_vehicle=None):
        super().__init__(parent)
        self.app = app
        self.controller = SortieController()
        self.vehicle_ctrl = VehicleController()
        self.employee_ctrl = EmployeeController()
        self.preselect_vehicle = preselect_vehicle
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()
        if preselect_vehicle:
            self.after(100, lambda: self._show_sortie_form(preselect_vehicle))

    def _create_widgets(self):
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(header, text="Réservations & Sorties", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')
        tk.Button(header, text="Nouvelle sortie", command=lambda: self._show_sortie_form(),
                 bg='#27ae60', fg='#000000', relief='flat').pack(side='right')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # En cours
        frame1 = tk.Frame(self.notebook, bg='white')
        self.notebook.add(frame1, text='En cours')
        tk.Label(frame1, text="Double-cliquez pour enregistrer le retour", font=('Helvetica', 9, 'italic'), bg='white', fg='#666666').pack(anchor='w', padx=10, pady=5)
        cols = [('vehicule', 'Véhicule', 150), ('employe', 'Conducteur', 150), ('date', 'Date sortie', 100),
                ('dest', 'Destination', 120), ('motif', 'Motif', 150), ('km', 'Km départ', 100)]
        self.tree_en_cours = FilterableTreeview(frame1, columns=cols, on_double_click=self._show_retour)
        self.tree_en_cours.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Historique
        frame2 = tk.Frame(self.notebook, bg='white')
        self.notebook.add(frame2, text='Historique')
        flt = tk.Frame(frame2, bg='white')
        flt.pack(fill='x', padx=10, pady=10)
        tk.Label(flt, text="Statut:", bg='white').pack(side='left')
        self.filter_statut = ttk.Combobox(flt, values=['', 'terminee', 'annulee'], state='readonly', width=12)
        self.filter_statut.pack(side='left', padx=5)
        self.filter_statut.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        cols2 = [('vehicule', 'Véhicule', 130), ('employe', 'Conducteur', 130), ('sortie', 'Sortie', 90),
                 ('retour', 'Retour', 90), ('dest', 'Destination', 100), ('km', 'Km', 80), ('duree', 'Durée', 80), ('statut', 'Statut', 80)]
        self.tree_hist = FilterableTreeview(frame2, columns=cols2)
        self.tree_hist.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree_hist.configure_tag('terminee', background='#d5f4e6')
        self.tree_hist.configure_tag('annulee', background='#fab1a0')
    
    def refresh(self):
        self.tree_en_cours.clear()
        for s in self.controller.get_en_cours():
            self.tree_en_cours.insert(values=(f"{s.immatriculation} ({s.marque})", f"{s.prenom} {s.nom}",
                s.date_sortie_reelle or s.date_sortie_prevue, s.destination or '-', s.motif or '-',
                f"{s.km_depart:,}".replace(',', ' ') if s.km_depart else '-'), tags=('en_cours', str(s.id)))
        
        statut = self.filter_statut.get() if hasattr(self, 'filter_statut') else ''
        self.tree_hist.clear()
        for s in self.controller.get_historique(statut if statut else None):
            km = f"{s.km_parcourus:,}".replace(',', ' ') if s.km_parcourus else '-'
            duree = '-'
            if s.date_sortie_reelle and s.date_retour_reelle:
                try:
                    d1, d2 = datetime.strptime(s.date_sortie_reelle, '%Y-%m-%d'), datetime.strptime(s.date_retour_reelle, '%Y-%m-%d')
                    days = (d2 - d1).days
                    duree = f"{days} jour{'s' if days > 1 else ''}"
                except:
                    pass
            self.tree_hist.insert(values=(f"{s.immatriculation} ({s.marque})", f"{s.prenom} {s.nom}",
                s.date_sortie_reelle or '-', s.date_retour_reelle or '-', s.destination or '-', km, duree, s.statut),
                tags=(s.statut, str(s.id)))
    
    def _show_sortie_form(self, preselect=None):
        SortieFormDialog(self, self.app, self.controller, self.vehicle_ctrl, self.employee_ctrl, preselect, self.refresh)
    
    def _show_retour(self):
        sid = self.tree_en_cours.get_selected_id(tag_index=1)
        if sid is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner une sortie")
            return
        RetourFormDialog(self, self.app, self.controller, sid, self.refresh)


class SortieFormDialog(BaseFormDialog):
    def __init__(self, parent, app, controller, vehicle_ctrl, employee_ctrl, preselect, refresh_cb):
        self.app = app
        self.controller = controller
        self.refresh_cb = refresh_cb
        self.preselect = preselect
        
        vehicles = vehicle_ctrl.get_available()
        self.vehicle_choices = [f"{v.immatriculation} - {v.marque} {v.modele}" for v in vehicles]
        self.vehicle_ids = {f"{v.immatriculation} - {v.marque} {v.modele}": v.id for v in vehicles}
        
        employees = employee_ctrl.get_authorized()
        self.employee_choices = [f"{e.matricule} - {e.full_name}" for e in employees]
        self.employee_ids = {f"{e.matricule} - {e.full_name}": e.id for e in employees}
        
        super().__init__(parent, "Nouvelle sortie", width=550, height=550)
        self._build_form()
    
    def _build_form(self):
        self.add_section_title("Véhicule et conducteur")
        self.add_combobox("Véhicule *", "vehicule", self.vehicle_choices)
        self.add_combobox("Conducteur *", "employe", self.employee_choices)
        if self.preselect:
            for c, vid in self.vehicle_ids.items():
                if vid == self.preselect:
                    self.set_value('vehicule', c)
                    break
        self.add_section_title("Informations")
        self.add_entry("Motif", "motif")
        self.add_entry("Destination", "destination")
        self.add_entry("Date sortie (AAAA-MM-JJ)", "date_sortie_prevue", default=date.today().isoformat())
        self.add_entry("Heure sortie (HH:MM)", "heure_sortie_prevue", default="08:00")
        self.add_entry("Date retour (AAAA-MM-JJ)", "date_retour_prevue")
        self.add_entry("Heure retour (HH:MM)", "heure_retour_prevue")
        self.add_entry("Km départ *", "km_depart")
        self.add_buttons(on_save=self._save, save_text="Enregistrer")
    
    def _save(self):
        data = {
            'vehicule_id': self.vehicle_ids.get(self.get_value('vehicule')),
            'employe_id': self.employee_ids.get(self.get_value('employe')),
            'motif': self.get_value('motif'), 'destination': self.get_value('destination'),
            'date_sortie_prevue': self.get_value('date_sortie_prevue'), 'heure_sortie_prevue': self.get_value('heure_sortie_prevue'),
            'date_retour_prevue': self.get_value('date_retour_prevue'), 'heure_retour_prevue': self.get_value('heure_retour_prevue'),
            'km_depart': self.get_value('km_depart')
        }
        result = self.controller.create_sortie(data, self.app.current_user.id)
        if result.success:
            self.show_success(result.message)
            if self.refresh_cb:
                self.refresh_cb()
            self.destroy()
        else:
            self.show_error(result.message)


class RetourFormDialog(BaseFormDialog):
    def __init__(self, parent, app, controller, sortie_id, refresh_cb):
        self.app = app
        self.controller = controller
        self.sortie = controller.get_by_id(sortie_id)
        self.refresh_cb = refresh_cb
        super().__init__(parent, "Retour de véhicule", width=500, height=450)
        self._build_form()
    
    def _build_form(self):
        s = self.sortie
        self.add_section_title("Informations de la sortie")
        info = tk.Frame(self.form_frame, bg='#ffffff')
        info.grid(row=self.current_row, column=0, columnspan=2, sticky='w', pady=5)
        self.current_row += 1
        tk.Label(info, text=f"Véhicule: {s.immatriculation} ({s.marque})", bg='#ffffff', fg='#000000').pack(anchor='w')
        tk.Label(info, text=f"Conducteur: {s.prenom} {s.nom}", bg='#ffffff', fg='#000000').pack(anchor='w')
        tk.Label(info, text=f"Km départ: {s.km_depart:,}".replace(',', ' '), bg='#ffffff', fg='#000000').pack(anchor='w')

        self.add_section_title("Retour")
        self.add_entry("Km retour *", "km_retour")
        self.add_combobox("État véhicule", "etat_retour", RETURN_STATES, default="bon")
        self.add_combobox("Niveau carburant", "niveau_carburant", FUEL_LEVELS, default="3/4")
        self.add_combobox("Nouveau statut", "nouveau_statut", ['disponible', 'en_maintenance', 'en_panne'], default="disponible")
        self.add_buttons(on_save=self._save, save_text="Valider")
    
    def _save(self):
        data = {
            'km_retour': self.get_value('km_retour'),
            'etat_retour': self.get_value('etat_retour'),
            'niveau_carburant': self.get_value('niveau_carburant'),
            'nouveau_statut': self.get_value('nouveau_statut')
        }
        result = self.controller.enregistrer_retour(self.sortie.id, data, self.app.current_user.id)
        if result.success:
            self.show_success(result.message)
            if self.refresh_cb:
                self.refresh_cb()
            self.destroy()
        else:
            self.show_error(result.message)
