import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from controllers import EmployeeController
from widgets import FilterableTreeview, AlertBanner


class EmployeesView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.ctrl = EmployeeController()
        self.setup_employees()
        self.refresh()

    def setup_employees(self) -> None:
        # titre
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(top, text="Employés", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(side='left')
        ctk.CTkButton(top, text="+ Ajouter", command=self.add,
                      fg_color='#2ecc71', hover_color='#27ae60', width=100).pack(side='right')

        # filtres
        flt = ctk.CTkFrame(self, fg_color='transparent')
        flt.pack(fill='x', padx=20, pady=5)

        ctk.CTkLabel(flt, text="Service:", text_color='#333333').pack(side='left')
        self.filter = ctk.CTkComboBox(flt, values=['Tous', 'Commercial', 'Technique', 'Administratif'],
                                       width=150, command=lambda e: self.refresh())
        self.filter.set('Tous')
        self.filter.pack(side='left', padx=5)

        self.only_auth = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(flt, text="Autorisés seulement", variable=self.only_auth,
                        command=self.refresh).pack(side='left', padx=10)

        ctk.CTkButton(flt, text="Actualiser", command=self.refresh,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='right')

        # alerte permis (utilisation du widget AlertBanner)
        self.alert = AlertBanner(self, "⚠️ Des permis expirent bientôt", bg_color='#f39c12')

        # liste (utilisation du widget FilterableTreeview)
        tree_frame = ctk.CTkFrame(self, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.tree_widget = FilterableTreeview(
            tree_frame,
            columns=[
                ('matricule', 'Matricule', 100),
                ('nom', 'Nom', 120),
                ('prenom', 'Prénom', 120),
                ('service', 'Service', 100),
                ('permis', 'N° Permis', 110),
                ('validite', 'Validité', 110),
                ('autorise', 'Autorisé', 80)
            ],
            on_double_click=self.detail,
            height=15
        )
        self.tree_widget.pack(fill='both', expand=True)

        # couleurs pour les tags
        self.tree_widget.configure_tag('ok', background='#d5f4e6')
        self.tree_widget.configure_tag('warning', background='#ffeaa7')
        self.tree_widget.configure_tag('expired', background='#ff7675')

        # référence directe pour compatibilité
        self.tree = self.tree_widget.tree

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', padx=20, pady=10)
        ctk.CTkButton(btns, text="Détails", command=self.detail,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Modifier", command=self.edit,
                      fg_color='#f39c12', hover_color='#e67e22', width=100).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Supprimer", command=self.delete,
                      fg_color='#e74c3c', hover_color='#c0392b', width=100).pack(side='left', padx=5)

    def get_tag(self, date_val):
        if not date_val:
            return 'ok'
        try:
            val = datetime.strptime(date_val, '%Y-%m-%d').date()
            days = (val - date.today()).days
            if days < 0:
                return 'expired'
            elif days < 30:
                return 'warning'
            else:
                return 'ok'
        except:
            return 'ok'

    def refresh(self) -> None:
        # vider avec le widget
        self.tree_widget.clear()

        # filtrer
        filters = {}
        service = self.filter.get()
        if service != 'Tous':
            filters['service'] = service
        if self.only_auth.get():
            filters['autorise_only'] = True

        # charger
        emps = self.ctrl.get_all(filters if filters else None)
        has_alert = False

        for e in emps:
            tag = self.get_tag(e.date_validite_permis)
            if tag in ('warning', 'expired'):
                has_alert = True

            auth = 'Oui' if e.autorise_conduire else 'Non'
            self.tree_widget.insert(
                values=(e.matricule, e.nom, e.prenom, e.service or '-',
                        e.num_permis or '-', e.date_validite_permis or '-', auth),
                tags=(tag, str(e.id))
            )

        # alerte avec AlertBanner
        if has_alert:
            self.alert.show(before=self.tree_widget.master)
        else:
            self.alert.hide()

    def add(self) -> None:
        EmpForm(self, self.app, self.ctrl, None, self.refresh)

    def edit(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un employé")
            return
        eid = int(self.tree.item(sel[0], 'tags')[1])
        emp = self.ctrl.get_by_id(eid)
        EmpForm(self, self.app, self.ctrl, emp, self.refresh)

    def delete(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un employé")
            return
        eid = int(self.tree.item(sel[0], 'tags')[1])
        emp = self.ctrl.get_by_id(eid)
        if not messagebox.askyesno("Confirmation", "Supprimer ?"):
            return
        res = self.ctrl.delete(eid, self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Supprimé")
            self.refresh()
        else:
            messagebox.showerror("Erreur", res.message)

    def detail(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        eid = int(self.tree.item(sel[0], 'tags')[1])
        EmpDetail(self, self.ctrl, eid)


class EmpForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, emp, cb) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.emp = emp
        self.cb = cb

        self.title("Modifier" if emp else "Nouvel employé")
        self.geometry("500x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        # champs
        ctk.CTkLabel(f, text="Matricule *").grid(row=0, column=0, sticky='w', pady=8)
        self.mat = ctk.CTkEntry(f, width=280)
        self.mat.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="Nom *").grid(row=1, column=0, sticky='w', pady=8)
        self.nom = ctk.CTkEntry(f, width=280)
        self.nom.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Prénom *").grid(row=2, column=0, sticky='w', pady=8)
        self.prenom = ctk.CTkEntry(f, width=280)
        self.prenom.grid(row=2, column=1, pady=8)

        ctk.CTkLabel(f, text="Service").grid(row=3, column=0, sticky='w', pady=8)
        self.service = ctk.CTkComboBox(f, values=['Commercial', 'Technique', 'Administratif'], width=280)
        self.service.grid(row=3, column=1, pady=8)

        ctk.CTkLabel(f, text="Téléphone").grid(row=4, column=0, sticky='w', pady=8)
        self.tel = ctk.CTkEntry(f, width=280)
        self.tel.grid(row=4, column=1, pady=8)

        ctk.CTkLabel(f, text="Email").grid(row=5, column=0, sticky='w', pady=8)
        self.email = ctk.CTkEntry(f, width=280)
        self.email.grid(row=5, column=1, pady=8)

        ctk.CTkLabel(f, text="N° Permis").grid(row=6, column=0, sticky='w', pady=8)
        self.permis = ctk.CTkEntry(f, width=280)
        self.permis.grid(row=6, column=1, pady=8)

        ctk.CTkLabel(f, text="Validité (AAAA-MM-JJ)").grid(row=7, column=0, sticky='w', pady=8)
        self.validite = ctk.CTkEntry(f, width=280)
        self.validite.grid(row=7, column=1, pady=8)

        self.auth = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(f, text="Autorisé à conduire", variable=self.auth).grid(row=8, column=1, sticky='w', pady=8)

        ctk.CTkLabel(f, text="Photo").grid(row=9, column=0, sticky='w', pady=8)
        photo_frame = ctk.CTkFrame(f, fg_color='transparent')
        photo_frame.grid(row=9, column=1, pady=8, sticky='w')
        self.photo = ctk.CTkEntry(photo_frame, width=200)
        self.photo.pack(side='left')
        ctk.CTkButton(photo_frame, text="...", width=30, command=self.browse_photo).pack(side='left', padx=5)

        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

        if emp:
            self.mat.insert(0, emp.matricule)
            self.nom.insert(0, emp.nom)
            self.prenom.insert(0, emp.prenom)
            self.service.set(emp.service or '')
            self.tel.insert(0, emp.telephone or '')
            self.email.insert(0, emp.email or '')
            self.permis.insert(0, emp.num_permis or '')
            self.validite.insert(0, emp.date_validite_permis or '')
            self.auth.set(emp.autorise_conduire)
            self.photo.insert(0, emp.photo_path or '')

    def browse_photo(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            self.photo.delete(0, 'end')
            self.photo.insert(0, path)

    def save(self) -> None:
        if not self.mat.get() or not self.nom.get() or not self.prenom.get():
            messagebox.showerror("Erreur", "Remplissez les champs obligatoires")
            return

        data = {
            'matricule': self.mat.get(),
            'nom': self.nom.get(),
            'prenom': self.prenom.get(),
            'service': self.service.get() or None,
            'telephone': self.tel.get() or None,
            'email': self.email.get() or None,
            'num_permis': self.permis.get() or None,
            'date_validite_permis': self.validite.get() or None,
            'autorise_conduire': 1 if self.auth.get() else 0,
            'photo_path': self.photo.get() or None
        }

        if self.emp:
            res = self.ctrl.update(self.emp.id, data, self.app.current_user.id)
        else:
            res = self.ctrl.create(data, self.app.current_user.id)

        if res.success:
            messagebox.showinfo("OK", "Enregistré")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)


class EmpDetail(ctk.CTkToplevel):
    def __init__(self, parent, ctrl, eid) -> None:
        super().__init__(parent)
        self.ctrl = ctrl
        self.e = ctrl.get_by_id(eid)
        self.eid = eid

        self.title(f"Fiche - {self.e.nom} {self.e.prenom}")
        self.geometry("700x600")
        self.transient(parent)
        self.grab_set()

        h = ctk.CTkFrame(self, fg_color='#ecf0f1', corner_radius=0)
        h.pack(fill='x')
        ctk.CTkLabel(h, text=f"{self.e.nom} {self.e.prenom} ({self.e.matricule})",
                     font=ctk.CTkFont(size=20, weight='bold'), text_color='#2c3e50').pack(side='left', padx=20, pady=15)

        color = '#2ecc71' if self.e.autorise_conduire else '#e74c3c'
        txt = 'Autorisé' if self.e.autorise_conduire else 'Non autorisé'
        badge = ctk.CTkLabel(h, text=txt, fg_color=color, corner_radius=6, text_color='white',
                             padx=15, pady=5)
        badge.pack(side='right', padx=20, pady=15)

        veh_aff = self.ctrl.dao.get_vehicle_affectation(eid)
        if veh_aff:
            veh_frame = ctk.CTkFrame(self, fg_color='#e8f4f8', corner_radius=8)
            veh_frame.pack(fill='x', padx=30, pady=10)
            ctk.CTkLabel(veh_frame, text=f"Véhicule de fonction: {veh_aff['immatriculation']} - {veh_aff['marque']} {veh_aff['modele']}",
                         font=ctk.CTkFont(weight='bold')).pack(pady=10)

        info = ctk.CTkFrame(self, fg_color='transparent')
        info.pack(fill='x', padx=30, pady=10)

        data = [
            ("Matricule:", self.e.matricule),
            ("Nom:", self.e.nom),
            ("Prénom:", self.e.prenom),
            ("Service:", self.e.service or '-'),
            ("Téléphone:", self.e.telephone or '-'),
            ("Email:", self.e.email or '-'),
            ("N° Permis:", self.e.num_permis or '-'),
            ("Validité:", self.e.date_validite_permis or '-')
        ]

        for i, (lbl, val) in enumerate(data):
            row = i // 2
            col = (i % 2) * 2
            ctk.CTkLabel(info, text=lbl, font=ctk.CTkFont(weight='bold'),
                         text_color='#7f8c8d').grid(row=row, column=col, sticky='e', padx=10, pady=8)
            ctk.CTkLabel(info, text=val, text_color='#2c3e50').grid(row=row, column=col + 1, sticky='w', padx=10, pady=8)

        ctk.CTkLabel(self, text="Historique des sorties", font=ctk.CTkFont(size=14, weight='bold'),
                     text_color='#2c3e50').pack(anchor='w', padx=30, pady=(10, 5))

        sorties_frame = ctk.CTkFrame(self, fg_color='transparent')
        sorties_frame.pack(fill='both', expand=True, padx=30, pady=5)

        sorties = self.ctrl.dao.get_sorties(eid)
        cols = ('date', 'vehicule', 'destination', 'km')
        tree = ttk.Treeview(sorties_frame, columns=cols, show='headings', height=6)
        tree.heading('date', text='Date')
        tree.heading('vehicule', text='Véhicule')
        tree.heading('destination', text='Destination')
        tree.heading('km', text='Km parcourus')
        tree.pack(fill='both', expand=True)

        for s in sorties:
            km = (s.get('km_retour', 0) or 0) - (s.get('km_depart', 0) or 0)
            tree.insert('', 'end', values=(
                s.get('date_sortie_reelle', '-'),
                f"{s['immatriculation']} ({s['marque']})",
                s.get('destination', '-'),
                f"{km} km" if km > 0 else '-'
            ))

        ctk.CTkButton(self, text="Fermer", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=120).pack(pady=15)