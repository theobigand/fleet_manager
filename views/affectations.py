import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
from controllers import AffectationController


class AffectationsView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.ctrl = AffectationController()
        self.setup_view()
        self.refresh()

    def setup_view(self) -> None:
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(top, text="Affectations permanentes", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(side='left')
        ctk.CTkButton(top, text="+ Nouvelle affectation", command=self.add,
                      fg_color='#2ecc71', hover_color='#27ae60', width=160).pack(side='right')

        tree_frame = ctk.CTkFrame(self, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        cols = ('vehicule', 'employe', 'date_debut')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree.heading('vehicule', text='Véhicule')
        self.tree.heading('employe', text='Employé')
        self.tree.heading('date_debut', text='Date début')

        self.tree.column('vehicule', width=250)
        self.tree.column('employe', width=200)
        self.tree.column('date_debut', width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', padx=20, pady=10)
        ctk.CTkButton(btns, text="Terminer l'affectation", command=self.end,
                      fg_color='#e74c3c', hover_color='#c0392b', width=160).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Actualiser", command=self.refresh,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='right')

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for a in self.ctrl.get_all_active():
            self.tree.insert('', 'end',
                             values=(f"{a['immatriculation']} - {a['marque']} {a['modele']}",
                                     f"{a['prenom']} {a['nom']} ({a['matricule']})",
                                     a['date_debut'] or '-'),
                             tags=(str(a['id']),))

    def add(self) -> None:
        AffectationForm(self, self.app, self.ctrl, self.refresh)

    def end(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionnez une affectation")
            return

        if not messagebox.askyesno("Confirmation", "Terminer cette affectation ?"):
            return

        aid = int(self.tree.item(sel[0], 'tags')[0])
        res = self.ctrl.end(aid, date.today().isoformat(), self.app.current_user.id)
        if res.success:
            messagebox.showinfo("OK", "Affectation terminée")
            self.refresh()
        else:
            messagebox.showerror("Erreur", res.message)


class AffectationForm(ctk.CTkToplevel):
    def __init__(self, parent, app, ctrl, cb) -> None:
        super().__init__(parent)
        self.app = app
        self.ctrl = ctrl
        self.cb = cb

        vehs = ctrl.get_available_vehicles()
        self.veh_dict = {f"{v.immatriculation} - {v.marque} {v.modele}": v.id for v in vehs}

        emps = ctrl.get_authorized_employees()
        self.emp_dict = {f"{e.matricule} - {e.nom} {e.prenom}": e.id for e in emps}

        self.title("Nouvelle affectation")
        self.geometry("500x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        if not self.veh_dict:
            messagebox.showwarning("Attention", "Aucun véhicule disponible pour affectation")
            self.destroy()
            return

        if not self.emp_dict:
            messagebox.showwarning("Attention", "Aucun employé autorisé à conduire")
            self.destroy()
            return

        f = ctk.CTkFrame(self, fg_color='transparent')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text="Véhicule *").grid(row=0, column=0, sticky='w', pady=8)
        self.veh = ctk.CTkComboBox(f, values=list(self.veh_dict.keys()), width=300)
        self.veh.grid(row=0, column=1, pady=8)

        ctk.CTkLabel(f, text="Employé *").grid(row=1, column=0, sticky='w', pady=8)
        self.emp = ctk.CTkComboBox(f, values=list(self.emp_dict.keys()), width=300)
        self.emp.grid(row=1, column=1, pady=8)

        ctk.CTkLabel(f, text="Date début *").grid(row=2, column=0, sticky='w', pady=8)
        self.date_debut = ctk.CTkEntry(f, width=300)
        self.date_debut.insert(0, date.today().isoformat())
        self.date_debut.grid(row=2, column=1, pady=8)

        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(fill='x', pady=15, padx=20)
        ctk.CTkButton(btns, text="Enregistrer", command=self.save,
                      fg_color='#2ecc71', hover_color='#27ae60', width=140).pack(side='right', padx=5)
        ctk.CTkButton(btns, text="Annuler", command=self.destroy,
                      fg_color='#95a5a6', hover_color='#7f8c8d', width=140).pack(side='right', padx=5)

    def save(self) -> None:
        if not self.veh.get() or not self.emp.get() or not self.date_debut.get():
            messagebox.showerror("Erreur", "Remplissez tous les champs")
            return

        if self.veh.get() not in self.veh_dict:
            messagebox.showerror("Erreur", "Sélectionnez un véhicule valide")
            return

        if self.emp.get() not in self.emp_dict:
            messagebox.showerror("Erreur", "Sélectionnez un employé valide")
            return

        res = self.ctrl.create(
            self.veh_dict[self.veh.get()],
            self.emp_dict[self.emp.get()],
            self.date_debut.get(),
            self.app.current_user.id
        )

        if res.success:
            messagebox.showinfo("OK", "Affectation créée")
            self.cb()
            self.destroy()
        else:
            messagebox.showerror("Erreur", res.message)
