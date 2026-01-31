import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from controllers import EmployeeController


class EmployeesView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='white')
        self.app = app
        self.ctrl = EmployeeController()
        self.setup_employees()
        self.refresh()

    def setup_employees(self):
        # titre
        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=20, pady=20)
        tk.Label(top, text="Employés", font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        tk.Button(top, text="+ Ajouter", command=self.add, bg='green', fg='white').pack(side='right')

        # filtres
        flt = tk.Frame(self, bg='white')
        flt.pack(fill='x', padx=20, pady=5)
        
        tk.Label(flt, text="Service:", bg='white').pack(side='left')
        self.filter = ttk.Combobox(flt, values=['Tous', 'Commercial', 'Technique', 'Administratif'], width=15)
        self.filter.set('Tous')
        self.filter.pack(side='left', padx=5)
        self.filter.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        self.only_auth = tk.BooleanVar(value=False)
        tk.Checkbutton(flt, text="Autorisés seulement", variable=self.only_auth, bg='white', command=self.refresh).pack(side='left', padx=10)
        
        tk.Button(flt, text="Actualiser", command=self.refresh, bg='blue', fg='white').pack(side='right')

        # alerte permis
        self.alert = tk.Frame(self, bg='orange', pady=10)
        tk.Label(self.alert, text="⚠️ Des permis expirent bientôt", font=('Arial', 12, 'bold'), bg='orange', fg='white').pack()

        # liste
        cols = ('matricule', 'nom', 'prenom', 'service', 'permis', 'validite', 'autorise')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)
        
        self.tree.heading('matricule', text='Matricule')
        self.tree.heading('nom', text='Nom')
        self.tree.heading('prenom', text='Prénom')
        self.tree.heading('service', text='Service')
        self.tree.heading('permis', text='N° Permis')
        self.tree.heading('validite', text='Validité')
        self.tree.heading('autorise', text='Autorisé')
        
        # couleurs
        self.tree.tag_configure('ok', background='lightgreen')
        self.tree.tag_configure('warning', background='yellow')
        self.tree.tag_configure('expired', background='red')
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree.bind('<Double-1>', lambda e: self.detail())

        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', padx=20, pady=10)
        tk.Button(btns, text="Détails", command=self.detail, bg='blue', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text="Modifier", command=self.edit, bg='orange', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text="Supprimer", command=self.delete, bg='red', fg='white').pack(side='left', padx=5)

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

    def refresh(self):
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
            self.alert.pack(fill='x', padx=20, pady=10, before=self.tree)
        else:
            self.alert.pack_forget()

    def add(self):
        EmpForm(self, self.app, self.ctrl, None, self.refresh)

    def edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un employé")
            return
        eid = int(self.tree.item(sel[0], 'tags')[1])
        emp = self.ctrl.get_by_id(eid)
        EmpForm(self, self.app, self.ctrl, emp, self.refresh)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez un employé")
            return
        eid = int(self.tree.item(sel[0], 'tags')[1])
        emp = self.ctrl.get_by_id(eid)
        if not messagebox.askyesno("Confirmation", f"Supprimer ?"):
            return
        res = self.ctrl.delete(eid, self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Supprimé")
            self.refresh()
        else:
            messagebox.showerror("Erreur", res.message)

    def detail(self):
        sel = self.tree.selection()
        if not sel:
            return
        eid = int(self.tree.item(sel[0], 'tags')[1])
        EmpDetail(self, self.ctrl, eid)


class EmpForm(tk.Toplevel):
    def __init__(self, parent, app, ctrl, emp, cb):
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.emp = emp
        self.cb = cb
        
        self.title("Modifier" if emp else "Nouvel employé")
        self.geometry("450x500")
        
        f = tk.Frame(self, bg='white', padx=20, pady=20)
        f.pack(fill='both', expand=True)
        
        # champs
        tk.Label(f, text="Matricule *", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.mat = tk.Entry(f, width=30)
        self.mat.grid(row=0, column=1, pady=5)
        
        tk.Label(f, text="Nom *", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.nom = tk.Entry(f, width=30)
        self.nom.grid(row=1, column=1, pady=5)
        
        tk.Label(f, text="Prénom *", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.prenom = tk.Entry(f, width=30)
        self.prenom.grid(row=2, column=1, pady=5)
        
        tk.Label(f, text="Service", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.service = ttk.Combobox(f, values=['Commercial', 'Technique', 'Administratif'], width=28)
        self.service.grid(row=3, column=1, pady=5)
        
        tk.Label(f, text="Téléphone", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.tel = tk.Entry(f, width=30)
        self.tel.grid(row=4, column=1, pady=5)
        
        tk.Label(f, text="Email", bg='white').grid(row=5, column=0, sticky='w', pady=5)
        self.email = tk.Entry(f, width=30)
        self.email.grid(row=5, column=1, pady=5)
        
        tk.Label(f, text="N° Permis", bg='white').grid(row=6, column=0, sticky='w', pady=5)
        self.permis = tk.Entry(f, width=30)
        self.permis.grid(row=6, column=1, pady=5)
        
        tk.Label(f, text="Validité (AAAA-MM-JJ)", bg='white').grid(row=7, column=0, sticky='w', pady=5)
        self.validite = tk.Entry(f, width=30)
        self.validite.grid(row=7, column=1, pady=5)
        
        self.auth = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text="Autorisé à conduire", variable=self.auth, bg='white').grid(row=8, column=1, sticky='w', pady=5)
        
        # boutons
        btns = tk.Frame(self, bg='white')
        btns.pack(fill='x', pady=10)
        tk.Button(btns, text="Enregistrer", command=self.save, bg='green', fg='white', width=12).pack(side='right', padx=20)
        tk.Button(btns, text="Annuler", command=self.destroy, bg='gray', fg='white', width=12).pack(side='right', padx=5)
        
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
    
    def save(self):
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


class EmpDetail(tk.Toplevel):
    def __init__(self, parent, ctrl, eid):
        super().__init__(parent)
        e = ctrl.get_by_id(eid)
        
        self.title(f"Fiche - {e.nom} {e.prenom}")
        self.geometry("600x400")
        
        # header
        h = tk.Frame(self, bg='lightgray', pady=15)
        h.pack(fill='x')
        tk.Label(h, text=f"{e.nom} {e.prenom} ({e.matricule})", 
                font=('Arial', 16, 'bold'), bg='lightgray').pack(side='left', padx=20)
        
        color = 'green' if e.autorise_conduire else 'red'
        txt = 'Autorisé' if e.autorise_conduire else 'Non autorisé'
        tk.Label(h, text=txt, bg=color, fg='white', padx=10, pady=5).pack(side='right', padx=20)
        
        # infos
        info = tk.Frame(self, bg='white', padx=20, pady=20)
        info.pack(fill='both', expand=True)
        
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
            tk.Label(info, text=lbl, font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=col, sticky='e', padx=5, pady=5)
            tk.Label(info, text=val, font=('Arial', 10), bg='white').grid(row=row, column=col+1, sticky='w', padx=5, pady=5)
        
        tk.Button(self, text="Fermer", command=self.destroy, bg='gray', fg='white').pack(pady=10)