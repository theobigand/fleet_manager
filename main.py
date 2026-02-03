import tkinter as tk
from tkinter import ttk, messagebox
import platform

from dao import BaseDAO
from controllers import AuthController
from views.login import LoginView
from views.dashboard import DashboardView
from views.vehicles import VehiclesView
from views.employees import EmployeesView
from views.affectations import AffectationsView
from views.reservations import ReservationsView
from views.maintenance import MaintenanceView
from views.documents import DocumentsView
from views.statistics import StatisticsView
from widgets import FilterableTreeview


class FleetApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gestion de Parc Automobile")
        self.geometry("1200x700")
        self.configure(bg='#ffffff')

        # Lancer en mode maximisé
        try:
            if platform.system() == 'Windows':
                self.state('zoomed')
            elif platform.system() == 'Darwin': # macOS
                self.state('zoomed')
            else:  # Linux
                self.attributes('-zoomed', True)
        except tk.TclError:
            pass

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TEntry', fieldbackground='white', foreground='black')
        style.configure('TCombobox', fieldbackground='white', foreground='black')
        style.configure('TNotebook', background='#ffffff')
        style.configure('TNotebook.Tab', background='#e0e0e0', foreground='black')
        style.map('TNotebook.Tab', background=[('selected', '#ffffff')])

        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.current_user = None
        self.auth_controller = AuthController()

        # Initialiser la BDD et l'admin par défaut
        BaseDAO.init_schema()
        self.auth_controller.init_default_admin()
        self._insert_test_data()

        self.show_login()

    def quit_app(self) -> None:
        self.quit()
    
    def _insert_test_data(self) -> None:
        """Insère des données de test si la BDD est vide"""
        from dao import VehicleDAO, EmployeeDAO, UserDAO
        
        vdao = VehicleDAO()
        if len(vdao.find_all()) > 0:
            return
        
        edao = EmployeeDAO()
        from models import Employee, Vehicle
        employees = [
            Employee(matricule='E001', nom='Dupont', prenom='Jean', service='Commercial', telephone='0612345678', autorise_conduire=1, num_permis='123456789', date_validite_permis='2026-12-31'),
            Employee(matricule='E002', nom='Martin', prenom='Marie', service='Technique', telephone='0623456789', autorise_conduire=1, num_permis='987654321', date_validite_permis='2025-03-15'),
            Employee(matricule='E003', nom='Bernard', prenom='Pierre', service='Direction', telephone='0634567890', autorise_conduire=1),
            Employee(matricule='E004', nom='Petit', prenom='Sophie', service='Commercial', telephone='0645678901', autorise_conduire=0),
            Employee(matricule='E005', nom='Robert', prenom='Luc', service='Technique', telephone='0656789012', autorise_conduire=1),
        ]
        for e in employees:
            edao.create(e)
        
        vehicles = [
            Vehicle(immatriculation='AA-123-BB', marque='Renault', modele='Clio', type_vehicule='Citadine', annee=2021, kilometrage_actuel=45000, carburant='Essence', statut='disponible', service_principal='Commercial'),
            Vehicle(immatriculation='CC-456-DD', marque='Peugeot', modele='308', type_vehicule='Berline', annee=2020, kilometrage_actuel=67000, carburant='Diesel', statut='disponible', service_principal='Technique'),
            Vehicle(immatriculation='EE-789-FF', marque='Citroën', modele='C3', type_vehicule='Citadine', annee=2022, kilometrage_actuel=23000, carburant='Essence', statut='en_sortie'),
            Vehicle(immatriculation='GG-012-HH', marque='Volkswagen', modele='Golf', type_vehicule='Berline', annee=2019, kilometrage_actuel=89000, carburant='Diesel', statut='en_maintenance'),
            Vehicle(immatriculation='II-345-JJ', marque='Toyota', modele='Yaris', type_vehicule='Citadine', annee=2023, kilometrage_actuel=12000, carburant='Hybride', statut='disponible', type_affectation='fonction'),
        ]
        for v in vehicles:
            vdao.create(v)
        
        udao = UserDAO()
        from models import User
        udao.create(User(username='gestionnaire', role='gestionnaire', nom='Gestionnaire', prenom='Test'), 'gest123')
        udao.create(User(username='employe', role='employe', nom='Employé', prenom='Test'), 'emp123')
    
    def show_login(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        LoginView(self, self).pack(fill='both', expand=True)
    
    def on_login_success(self, user) -> None:
        self.current_user = user
        self.show_main()
    
    def show_main(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        
        sidebar = tk.Frame(self, bg='#f5f5f5', width=220)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Fleet Manager", font=('Helvetica', 14, 'bold'), bg='#f5f5f5', fg='#000000').pack(pady=(20, 5))

        tk.Frame(sidebar, bg='#cccccc', height=1).pack(fill='x', pady=20)

        tk.Label(sidebar, text=f"{self.current_user.full_name}", font=('Helvetica', 10), bg='#f5f5f5', fg='#333333').pack()
        tk.Label(sidebar, text=f"({self.current_user.role})", font=('Helvetica', 9), bg='#f5f5f5', fg='#666666').pack(pady=(0, 15))

        menus = [('Tableau de bord', 'dashboard'), ('Véhicules', 'vehicles'), ('Employés', 'employees'),
                 ('Affectations', 'affectations'), ('Réservations', 'reservations'), ('Maintenance', 'maintenance'),
                 ('Documents', 'documents'), ('Statistiques', 'statistics')]

        if self.current_user.role == 'admin':
            menus.append(('Administration', 'admin'))

        for label, view in menus:
            if self.current_user.role == 'employe' and view not in ('dashboard', 'reservations'):
                continue
            if self.current_user.role == 'gestionnaire' and view == 'admin':
                continue
            btn = tk.Button(sidebar, text=label, anchor='w', padx=20, pady=10,
                           bg='#f5f5f5', fg='#000000', relief='flat', font=('Helvetica', 10),
                           activebackground='#e0e0e0', cursor='hand2',
                           command=lambda v=view: self.navigate_to(v))
            btn.pack(fill='x')

        quit_btn = tk.Button(sidebar, text="Quitter", bg='#d0d0d0', fg='#000000',
                 relief='flat', pady=10, cursor='hand2')
        quit_btn.config(command=self.quit_app)
        quit_btn.pack(side='bottom', fill='x')
        tk.Button(sidebar, text="Déconnexion", command=self.logout, bg='#e74c3c', fg='#000000',
                 relief='flat', pady=10, cursor='hand2').pack(side='bottom', fill='x')

        self.content_frame = tk.Frame(self, bg='#ffffff')
        self.content_frame.pack(side='left', fill='both', expand=True)
        
        self.navigate_to('dashboard')
    
    def navigate_to(self, view_name, **kwargs) -> None:
        for w in self.content_frame.winfo_children():
            w.destroy()
        
        views = {
            'dashboard': DashboardView,
            'vehicles': VehiclesView,
            'employees': EmployeesView,
            'affectations': AffectationsView,
            'reservations': ReservationsView,
            'maintenance': MaintenanceView,
            'documents': DocumentsView,
            'statistics': StatisticsView,
            'admin': self._show_admin_view,
        }
        
        view_class = views.get(view_name)
        if view_class:
            if callable(view_class) and view_name == 'admin':
                view_class()
            else:
                view_class(self.content_frame, self, **kwargs).pack(fill='both', expand=True)
    
    def _show_admin_view(self) -> None:
        frame = tk.Frame(self.content_frame, bg='#ffffff')
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Administration", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(anchor='w', padx=20, pady=20)

        notebook = ttk.Notebook(frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        logs_frame = tk.Frame(notebook, bg='white')
        notebook.add(logs_frame, text='Logs')
        cols = [('date', 'Date', 150), ('user', 'Utilisateur', 120), ('action', 'Action', 150), ('details', 'Détails', 300)]
        tree_logs = FilterableTreeview(logs_frame, columns=cols)
        tree_logs.pack(fill='both', expand=True, padx=10, pady=10)
        for log in self.auth_controller.get_logs(200):
            tree_logs.insert(values=(log.date_action, log.username or '-', log.action, log.details or '-'))

        users_frame = tk.Frame(notebook, bg='white')
        notebook.add(users_frame, text='Utilisateurs')

        toolbar = tk.Frame(users_frame, bg='white')
        toolbar.pack(fill='x', padx=10, pady=10)
        tk.Button(toolbar, text="+ Nouvel utilisateur", command=lambda: self._show_user_form(tree_users),
                  bg='#2ecc71', fg='black', relief='flat', padx=15, pady=5, cursor='hand2').pack(side='left')
        tk.Button(toolbar, text="Désactiver", command=lambda: self._delete_user(tree_users),
                  bg='#e74c3c', fg='black', relief='flat', padx=15, pady=5, cursor='hand2').pack(side='left', padx=10)

        cols2 = [('username', 'Username', 120), ('role', 'Rôle', 100), ('nom', 'Nom', 150), ('prenom', 'Prénom', 150), ('email', 'Email', 200)]
        tree_users = FilterableTreeview(users_frame, columns=cols2)
        tree_users.pack(fill='both', expand=True, padx=10, pady=10)
        for u in self.auth_controller.get_all_users():
            tree_users.insert(values=(u.username, u.role, u.nom or '-', u.prenom or '-', u.email or '-'))

    def _show_user_form(self, tree) -> None:
        win = tk.Toplevel(self)
        win.title("Nouvel utilisateur")
        win.geometry("400x350")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        f = tk.Frame(win, bg='white')
        f.pack(fill='both', expand=True, padx=20, pady=20)

        entries = {}
        fields = [('username', "Nom d'utilisateur *"), ('password', 'Mot de passe *'),
                  ('role', 'Rôle *'), ('nom', 'Nom'), ('prenom', 'Prénom'), ('email', 'Email')]

        for i, (key, label) in enumerate(fields):
            tk.Label(f, text=label, bg='white', fg='#333333').grid(row=i, column=0, sticky='w', pady=8)
            if key == 'role':
                entries[key] = ttk.Combobox(f, values=['admin', 'gestionnaire', 'employe'], state='readonly', width=27)
                entries[key].set('employe')
            elif key == 'password':
                entries[key] = ttk.Entry(f, width=30, show='*')
            else:
                entries[key] = ttk.Entry(f, width=30)
            entries[key].grid(row=i, column=1, pady=8, padx=10)

        def save():
            data = {
                'username': entries['username'].get().strip(),
                'role': entries['role'].get(),
                'nom': entries['nom'].get().strip() or None,
                'prenom': entries['prenom'].get().strip() or None,
                'email': entries['email'].get().strip() or None
            }
            password = entries['password'].get()

            result = self.auth_controller.create_user(data, password, self.current_user.id)
            if result.success:
                messagebox.showinfo("Succès", "Utilisateur créé")
                for item in tree.tree.get_children():
                    tree.tree.delete(item)
                for u in self.auth_controller.get_all_users():
                    tree.insert(values=(u.username, u.role, u.nom or '-', u.prenom or '-', u.email or '-'))
                win.destroy()
            else:
                messagebox.showerror("Erreur", result.message)

        btns = tk.Frame(win, bg='white')
        btns.pack(fill='x', pady=15, padx=20)
        tk.Button(btns, text="Enregistrer", command=save, bg='#2ecc71', fg='black',
                  relief='flat', padx=20, pady=8, cursor='hand2').pack(side='right', padx=5)
        tk.Button(btns, text="Annuler", command=win.destroy, bg='#95a5a6', fg='black',
                  relief='flat', padx=20, pady=8, cursor='hand2').pack(side='right', padx=5)

    def _delete_user(self, tree) -> None:
        selection = tree.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur")
            return

        item = tree.tree.item(selection[0])
        username = item['values'][0]

        if not messagebox.askyesno("Confirmation", f"Désactiver l'utilisateur '{username}' ?"):
            return

        result = self.auth_controller.delete_user(username, self.current_user.id)
        if result.success:
            messagebox.showinfo("Succès", "Utilisateur désactivé")
            for item in tree.tree.get_children():
                tree.tree.delete(item)
            for u in self.auth_controller.get_all_users():
                tree.insert(values=(u.username, u.role, u.nom or '-', u.prenom or '-', u.email or '-'))
        else:
            messagebox.showerror("Erreur", result.message)

    def logout(self) -> None:
        self.auth_controller.logout(self.current_user.id)
        self.current_user = None
        self.show_login()


if __name__ == '__main__':
    app = FleetApp()
    app.mainloop()
