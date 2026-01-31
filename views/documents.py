# views/documents.py - Documents véhicules (MVC)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import os, subprocess, sys

from controllers import DocumentController, VehicleController
from widgets import FilterableTreeview, BaseFormDialog
from config import DOCUMENT_TYPES


class DocumentsView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = DocumentController()
        self.vehicle_ctrl = VehicleController()
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(header, text="Documents", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            tk.Button(header, text="Nouveau", command=lambda: self._show_form(), bg='#27ae60', fg='#000000', relief='flat').pack(side='right')

        flt = tk.Frame(self, bg='#ffffff')
        flt.pack(fill='x', padx=20, pady=10)
        tk.Label(flt, text="Véhicule:", bg='#ffffff', fg='#000000').pack(side='left')
        vehicles = self.vehicle_ctrl.get_all()
        self.veh_filter = ttk.Combobox(flt, values=[''] + [v.immatriculation for v in vehicles], state='readonly', width=15)
        self.veh_filter.pack(side='left', padx=5)
        self.veh_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        tk.Label(flt, text="Type:", bg='#ffffff', fg='#000000').pack(side='left', padx=(15, 0))
        self.type_filter = ttk.Combobox(flt, values=[''] + DOCUMENT_TYPES, state='readonly', width=15)
        self.type_filter.pack(side='left', padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        tk.Button(flt, text="Reset", command=self._reset, bg='#cccccc', fg='#000000', relief='flat').pack(side='left', padx=15)
        
        cols = [('vehicule', 'Véhicule', 150), ('type', 'Type', 150), ('emission', 'Émission', 100),
                ('echeance', 'Échéance', 100), ('jours', 'Jours', 80), ('fichier', 'Fichier', 150), ('desc', 'Description', 150)]
        self.tree = FilterableTreeview(self, columns=cols, on_double_click=self._open_file, on_right_click=self._show_menu)
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree.configure_tag('ok', background='#d5f4e6')
        self.tree.configure_tag('warning', background='#ffeaa7')
        self.tree.configure_tag('expired', background='#fab1a0')
        
        self.ctx = tk.Menu(self, tearoff=0)
        self.ctx.add_command(label="Ouvrir", command=self._open_file)
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            self.ctx.add_command(label="Modifier", command=self._edit)
            self.ctx.add_separator()
            self.ctx.add_command(label="Supprimer", command=self._delete)
    
    def _show_menu(self, event):
        self.ctx.post(event.x_root, event.y_root)
    
    def _reset(self):
        self.veh_filter.set('')
        self.type_filter.set('')
        self.refresh()
    
    def _get_tag(self, date_ech):
        if not date_ech:
            return 'ok'
        try:
            days = (datetime.strptime(date_ech, '%Y-%m-%d').date() - date.today()).days
            return 'expired' if days < 0 else 'warning' if days < 30 else 'ok'
        except:
            return 'ok'
    
    def refresh(self):
        veh = self.veh_filter.get()
        typ = self.type_filter.get()
        self.tree.clear()
        for d in self.controller.get_all(veh or None, typ or None):
            jours = '-'
            if d.date_echeance:
                try:
                    jours = str((datetime.strptime(d.date_echeance, '%Y-%m-%d').date() - date.today()).days)
                except:
                    pass
            fichier = os.path.basename(d.chemin_fichier) if d.chemin_fichier else '-'
            self.tree.insert(values=(f"{d.immatriculation} ({d.marque})", d.type_document, d.date_emission or '-',
                d.date_echeance or '-', jours, fichier, d.description or '-'), tags=(self._get_tag(d.date_echeance), str(d.id)))
    
    def _show_form(self, doc=None):
        DocumentFormDialog(self, self.app, self.controller, self.vehicle_ctrl, doc, self.refresh)
    
    def _edit(self):
        did = self.tree.get_selected_id(tag_index=1)
        if did:
            self._show_form(self.controller.get_by_id(did))
    
    def _delete(self):
        did = self.tree.get_selected_id(tag_index=1)
        if did and messagebox.askyesno("Confirmation", "Supprimer ce document ?"):
            self.controller.delete(did, self.app.current_user.id)
            self.refresh()
    
    def _open_file(self):
        did = self.tree.get_selected_id(tag_index=1)
        if not did:
            return
        doc = self.controller.get_by_id(did)
        if not doc or not doc.chemin_fichier:
            messagebox.showinfo("Info", "Aucun fichier associé")
            return
        if not os.path.exists(doc.chemin_fichier):
            messagebox.showerror("Erreur", "Fichier introuvable")
            return
        try:
            if sys.platform == 'win32':
                os.startfile(doc.chemin_fichier)
            elif sys.platform == 'darwin':
                subprocess.run(['open', doc.chemin_fichier])
            else:
                subprocess.run(['xdg-open', doc.chemin_fichier])
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class DocumentFormDialog(BaseFormDialog):
    def __init__(self, parent, app, controller, vehicle_ctrl, doc, refresh_cb):
        self.app = app
        self.controller = controller
        self.doc = doc
        self.refresh_cb = refresh_cb
        vehicles = vehicle_ctrl.get_all()
        self.vehicle_choices = [f"{v.immatriculation} - {v.marque}" for v in vehicles]
        self.vehicle_ids = {f"{v.immatriculation} - {v.marque}": v.id for v in vehicles}
        super().__init__(parent, "Modifier" if doc else "Nouveau document", width=500, height=450)
        self._build_form()
        if doc:
            self._load_data()
    
    def _build_form(self):
        self.add_section_title("Document")
        self.add_combobox("Véhicule *", "vehicule", self.vehicle_choices)
        self.add_combobox("Type *", "type_document", DOCUMENT_TYPES)
        self.add_entry("Date émission", "date_emission")
        self.add_entry("Date échéance", "date_echeance")
        self.add_file_picker("Fichier", "chemin_fichier", [("Documents", "*.pdf *.jpg *.png"), ("Tous", "*.*")])
        self.add_text("Description", "description", height=3)
        self.add_buttons(on_save=self._save)
    
    def _load_data(self):
        for c, vid in self.vehicle_ids.items():
            if vid == self.doc.vehicule_id:
                self.set_value('vehicule', c)
                break
        self.set_value('type_document', self.doc.type_document or '')
        self.set_value('date_emission', self.doc.date_emission or '')
        self.set_value('date_echeance', self.doc.date_echeance or '')
        self.set_value('chemin_fichier', self.doc.chemin_fichier or '')
        self.set_value('description', self.doc.description or '')
    
    def _save(self):
        data = {'vehicule_id': self.vehicle_ids.get(self.get_value('vehicule')),
                'type_document': self.get_value('type_document'), 'date_emission': self.get_value('date_emission'),
                'date_echeance': self.get_value('date_echeance'), 'chemin_fichier': self.get_value('chemin_fichier'),
                'description': self.get_value('description')}
        if self.doc:
            result = self.controller.update(self.doc.id, data, self.app.current_user.id)
        else:
            result = self.controller.create(data, self.app.current_user.id)
        if result.success:
            self.show_success(result.message)
            if self.refresh_cb:
                self.refresh_cb()
            self.destroy()
        else:
            self.show_error(result.message)
