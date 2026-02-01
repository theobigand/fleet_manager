import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, date
from controllers import EmployeeController


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

        # alerte permis
        self.alert = ctk.CTkFrame(self, fg_color='#f39c12', corner_radius=8)
        ctk.CTkLabel(self.alert, text="⚠️ Des permis expirent bientôt",
                     font=ctk.CTkFont(size=14, weight='bold'), text_color='white').pack(pady=10)

        # liste
        tree_frame = ctk.CTkFrame(self, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        cols = ('matricule', 'nom', 'prenom', 'service', 'permis', 'validite', 'autorise')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)

        self.tree.heading('matricule', text='Matricule')
        self.tree.heading('nom', text='Nom')
        self.tree.heading('prenom', text='Prénom')
        self.tree.heading('service', text='Service')
        self.tree.heading('permis', text='N° Permis')
        self.tree.heading('validite', text='Validité')
        self.tree.heading('autorise', text='Autorisé')

        # couleurs
        self.tree.tag_configure('ok', background='#d5f4e6')
        self.tree.tag_configure('warning', background='#ffeaa7')
        self.tree.tag_configure('expired', background='#ff7675')

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
        # vider
        for item in self.tree.get_children():
            self.tree.delete(item)

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
            self.tree.insert('', 'end',
                             values=(e.matricule, e.nom, e.prenom, e.service or '-',
                                     e.num_permis or '-', e.date_validite_permis or '-', auth),
                             tags=(tag, str(e.id)))

        # alerte
        if has_alert:
            self.alert.pack(fill='x', padx=20, pady=10, before=self.tree.master)
        else:
            self.alert.pack_forget()

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
        self.geometry("500x580")
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

        # boutons
        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

        # charger
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
            'autorise_conduire': 1 if self.auth.get() else 0
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
        e = ctrl.get_by_id(eid)

        self.title(f"Fiche - {e.nom} {e.prenom}")
        self.geometry("650x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # header
        h = ctk.CTkFrame(self, fg_color='#ecf0f1', corner_radius=0)
        h.pack(fill='x')
        ctk.CTkLabel(h, text=f"{e.nom} {e.prenom} ({e.matricule})",
                     font=ctk.CTkFont(size=20, weight='bold'), text_color='#2c3e50').pack(side='left', padx=20, pady=15)

        color = '#2ecc71' if e.autorise_conduire else '#e74c3c'
        txt = 'Autorisé' if e.autorise_conduire else 'Non autorisé'
        badge = ctk.CTkLabel(h, text=txt, fg_color=color, corner_radius=6, text_color='white',
                             padx=15, pady=5)
        badge.pack(side='right', padx=20, pady=15)

        # infos
        info = ctk.CTkFrame(self, fg_color='transparent')
        info.pack(fill='both', expand=True, padx=30, pady=20)

        data = [
            ("Matricule:", e.matricule),
            ("Nom:", e.nom),
            ("Prénom:", e.prenom),
            ("Service:", e.service or '-'),
            ("Téléphone:", e.telephone or '-'),
            ("Email:", e.email or '-'),
            ("N° Permis:", e.num_permis or '-'),
            ("Validité:", e.date_validite_permis or '-')
        ]

        for i, (lbl, val) in enumerate(data):
            row = i // 2
            col = (i % 2) * 2
            ctk.CTkLabel(info, text=lbl, font=ctk.CTkFont(weight='bold'),
                         text_color='#7f8c8d').grid(row=row, column=col, sticky='e', padx=10, pady=8)
            ctk.CTkLabel(info, text=val, text_color='#2c3e50').grid(row=row, column=col + 1, sticky='w', padx=10, pady=8)

        ctk.CTkButton(self, text="Fermer", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=120).pack(pady=15)