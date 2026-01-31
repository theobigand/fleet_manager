import tkinter as tk
from tkinter import messagebox
from controllers import AuthController

class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = AuthController()
        self.configure()
        self.setup_login()
    
    def setup_login(self):

        # titre principal
        titre = tk.Label(self, text="Gestion de Parc Automobile", font=('Arial', 18, 'bold'))
        titre.pack(pady=30)
        
        # connexion
        sous_titre = tk.Label(self, text="Connexion", font=('Arial', 14))
        sous_titre.pack(pady=10)
        
        # frame pour le formulaire
        form_frame = tk.Frame(self, padx=30, pady=30)
        form_frame.pack(pady=20)
        
        # username
        label_user = tk.Label(form_frame, text="Nom d'utilisateur:")
        label_user.grid(row=0, column=0, sticky='w', pady=5)
        self.username_var = tk.StringVar()
        entry_user = tk.Entry(form_frame, textvariable=self.username_var, width=25)
        entry_user.grid(row=1, column=0, pady=5)
        
        # password
        label_pass = tk.Label(form_frame, text="Mot de passe:")
        label_pass.grid(row=2, column=0, sticky='w', pady=(15,5))
        self.password_var = tk.StringVar()
        entry_pass = tk.Entry(form_frame, textvariable=self.password_var, width=25, show='*')
        entry_pass.grid(row=3, column=0, pady=5)
        entry_pass.bind('<Return>', lambda e: self.login())

        # boutons
        # login
        btn_login = tk.Button(form_frame, text="Se connecter", command=self.login, bg='#4CAF50', width=20)
        btn_login.grid(row=4, column=0, pady=15)

        # quit
        btn_quit = tk.Button(form_frame, text="Quitter", command=self.app.quit_app, width=20)
        btn_quit.grid(row=5, column=0)
        
        info = tk.Label(self, text="Compte test: admin / admin123")
        info.pack(pady=10)
    
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if username == "" or password == "":
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
            return
        
        result = self.controller.login(username, password)
        
        if result.success:
            self.app.on_login_success(result.data)
        else:
            messagebox.showerror("Erreur", result.message)
            self.password_var.set("")