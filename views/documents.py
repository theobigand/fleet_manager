import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import subprocess
import sys

from controllers import DocumentController, VehicleController


class DocumentsView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='white')
        self.app = app
        self.controller = DocumentController()
        self.vehicle_ctrl = VehicleController()
        self.setup_document()
        self.refresh()

    def setup_document(self):
        header = tk.Frame(self, bg='white')
        header.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header, text="Documents", font=('Arial', 18, 'bold'), 
                bg='white').pack(side='left')
        
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            tk.Button(header, text="Nouveau", command=self.add_document, 
                     bg='#2ecc71', fg='white').pack(side='right')

        # filtres
        filter_frame = tk.Frame(self, bg='white')
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(filter_frame, text="Véhicule:", bg='white').pack(side='left')
        vehicles = self.vehicle_ctrl.get_all()
        self.veh_filter = ttk.Combobox(filter_frame, 
            values=['Tous'] + [v.immatriculation for v in vehicles], 
            state='readonly', width=15)
        self.veh_filter.set('Tous')
        self.veh_filter.pack(side='left', padx=5)
        self.veh_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        tk.Label(filter_frame, text="Type:", bg='white').pack(side='left', padx=(15, 0))
        types = ['Assurance', 'Contrôle technique', 'Carte grise', 'Vignette', 'Leasing']
        self.type_filter = ttk.Combobox(filter_frame, 
            values=['Tous'] + types, state='readonly', width=15)
        self.type_filter.set('Tous')
        self.type_filter.pack(side='left', padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # treeview
        tree_frame = tk.Frame(self, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('vehicule', 'type', 'emission', 'echeance', 'jours', 'fichier')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('vehicule', text='Véhicule')
        self.tree.heading('type', text='Type')
        self.tree.heading('emission', text='Émission')
        self.tree.heading('echeance', text='Échéance')
        self.tree.heading('jours', text='Jours restants')
        self.tree.heading('fichier', text='Fichier')
        
        self.tree.column('vehicule', width=150)
        self.tree.column('type', width=120)
        self.tree.column('emission', width=100)
        self.tree.column('echeance', width=100)
        self.tree.column('jours', width=100)
        self.tree.column('fichier', width=150)
        
        self.tree.tag_configure('ok', background='#d5f4e6')
        self.tree.tag_configure('warning', background='#ffeaa7')
        self.tree.tag_configure('expired', background='#fab1a0')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # boutons
        if self.app.current_user.role in ('admin', 'gestionnaire'):
            btn_frame = tk.Frame(self, bg='white')
            btn_frame.pack(fill='x', padx=20, pady=10)
            tk.Button(btn_frame, text="Ouvrir fichier", command=self.open_file, 
                     bg='#3498db', fg='white').pack(side='left', padx=5)
            tk.Button(btn_frame, text="Modifier", command=self.edit_document, 
                     bg='#f39c12', fg='white').pack(side='left', padx=5)
            tk.Button(btn_frame, text="Supprimer", command=self.delete_document, 
                     bg='#e74c3c', fg='white').pack(side='left', padx=5)

    def refresh(self):
        """Recharge les documents"""
        
        # récupérer filtres
        veh_filter = self.veh_filter.get()
        veh_filter = None if veh_filter == 'Tous' else veh_filter
        
        type_filter = self.type_filter.get()
        type_filter = None if type_filter == 'Tous' else type_filter
    
        # vider treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # charger documents
        documents = self.controller.get_all(veh_filter, type_filter)
        
        for doc in documents:
            # calculer jours restants
            jours = '-'
            tag = 'ok'
            
            if doc.date_echeance:
                try:
                    ech_date = datetime.strptime(doc.date_echeance, '%Y-%m-%d').date()
                    days_left = (ech_date - date.today()).days
                    jours = str(days_left)
                    
                    if days_left < 0:
                        tag = 'expired'
                    elif days_left < 30:
                        tag = 'warning'
                except:
                    pass
            
            fichier = os.path.basename(doc.chemin_fichier) if doc.chemin_fichier else '-'
            
            self.tree.insert('', 'end', 
                           values=(
                               f"{doc.immatriculation} ({doc.marque})",
                               doc.type_document,
                               doc.date_emission or '-',
                               doc.date_echeance or '-',
                               jours,
                               fichier
                           ),
                           tags=(tag, str(doc.id)))

    def add_document(self):
        """Ajouter un document"""
        DocumentFormDialog(self, self.app, self.controller, 
                          self.vehicle_ctrl, None, self.refresh)

    def edit_document(self):
        """Modifier un document"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un document")
            return
        
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if len(tags) > 1:
            doc_id = int(tags[1])
            doc = self.controller.get_by_id(doc_id)
            DocumentFormDialog(self, self.app, self.controller, 
                             self.vehicle_ctrl, doc, self.refresh)

    def delete_document(self):
        """Supprimer un document"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un document")
            return
        
        if not messagebox.askyesno("Confirmation", "Supprimer ce document ?"):
            return
        
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if len(tags) > 1:
            doc_id = int(tags[1])
            result = self.controller.delete(doc_id, self.app.current_user.id)
            if result.success:
                messagebox.showinfo("Succès", result.message)
                self.refresh()
            else:
                messagebox.showerror("Erreur", result.message)

    def open_file(self):
        """Ouvrir le fichier du document"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if len(tags) > 1:
            doc_id = int(tags[1])
            doc = self.controller.get_by_id(doc_id)
            
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
                messagebox.showerror("Erreur", f"Impossible d'ouvrir: {e}")


class DocumentFormDialog(tk.Toplevel):
    def __init__(self, parent, app, controller, vehicle_ctrl, doc, refresh_cb):
        super().__init__(parent)
        self.app = app
        self.controller = controller
        self.doc = doc
        self.refresh_cb = refresh_cb
        
        # récupérer véhicules
        vehicles = vehicle_ctrl.get_all()
        self.vehicle_choices = {f"{v.immatriculation} - {v.marque}": v.id for v in vehicles}
        
        self.title("Modifier document" if doc else "Nouveau document")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        
        self.create_form()
        
        if doc:
            self.load_data()
    
    def create_form(self):
        """Créer le formulaire"""
        form_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # vehicule
        tk.Label(form_frame, text="Véhicule *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.combo_vehicule = ttk.Combobox(form_frame, values=list(self.vehicle_choices.keys()), state='readonly', width=30)
        self.combo_vehicule.grid(row=0, column=1, pady=5)

        # type
        tk.Label(form_frame, text="Type *", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.combo_type = ttk.Combobox(form_frame, values=['Assurance', 'CT', 'Carte grise', 'Vignette'], state='readonly', width=30)
        self.combo_type.grid(row=1, column=1, pady=5)

        # dates
        tk.Label(form_frame, text="Date émission", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.entry_emission = tk.Entry(form_frame, width=32)
        self.entry_emission.grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Date échéance", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.entry_echeance = tk.Entry(form_frame, width=32)
        self.entry_echeance.grid(row=3, column=1, pady=5)

        # fichier
        tk.Label(form_frame, text="Fichier", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        ff = tk.Frame(form_frame, bg='white')
        ff.grid(row=4, column=1, pady=5, sticky='w')
        self.entry_fichier = tk.Entry(ff, width=22)
        self.entry_fichier.pack(side='left')
        tk.Button(ff, text="...", command=self.browse_file).pack(side='left', padx=5)

        # description
        tk.Label(form_frame, text="Description", bg='white').grid(row=5, column=0, sticky='nw', pady=5)
        self.text_description = tk.Text(form_frame, width=30, height=4)
        self.text_description.grid(row=5, column=1, pady=5)
        
        # boutons
        btn_frame = tk.Frame(self, bg='white', pady=10)
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="Enregistrer", command=self.save, 
                 bg='#2ecc71', fg='white', width=15).pack(side='right', padx=20)
        tk.Button(btn_frame, text="❌ Annuler", command=self.destroy, 
                 bg='#95a5a6', fg='white', width=15).pack(side='right', padx=5)
    
    def browse_file(self):
        """Parcourir pour sélectionner un fichier"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un document",
            filetypes=[("Documents", "*.pdf *.jpg *.png"), ("Tous", "*.*")]
        )
        if filename:
            self.entry_fichier.delete(0, 'end')
            self.entry_fichier.insert(0, filename)
    
    def load_data(self):
        """Charger les données du document"""

        for key, vid in self.vehicle_choices.items():
            if vid == self.doc.vehicule_id:
                self.combo_vehicule.set(key)
                break
        
        self.combo_type.set(self.doc.type_document or '')
        self.entry_emission.insert(0, self.doc.date_emission or '')
        self.entry_echeance.insert(0, self.doc.date_echeance or '')
        self.entry_fichier.insert(0, self.doc.chemin_fichier or '')
        self.text_description.insert('1.0', self.doc.description or '')
    

    
    def save(self):
        """Enregistrer le document"""
        # récupérer les valeurs
        vehicule_key = self.combo_vehicule.get()
        if not vehicule_key:
            messagebox.showerror("Erreur", "Sélectionnez un véhicule")
            return
        
        type_doc = self.combo_type.get()
        if not type_doc:
            messagebox.showerror("Erreur", "Sélectionnez un type")
            return
        
        data = {
            'vehicule_id': self.vehicle_choices[vehicule_key],
            'type_document': type_doc,
            'date_emission': self.entry_emission.get().strip() or None,
            'date_echeance': self.entry_echeance.get().strip() or None,
            'chemin_fichier': self.entry_fichier.get().strip() or None,
            'description': self.text_description.get('1.0', 'end').strip() or None
        }
        
        if self.doc:
            result = self.controller.update(self.doc.id, data, self.app.current_user.id)
        else:
            result = self.controller.create(data, self.app.current_user.id)
        
        if result.success:
            messagebox.showinfo("Succès", result.message)
            if self.refresh_cb:
                self.refresh_cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", result.message)