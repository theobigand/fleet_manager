# views/login.py - Écran de connexion (MVC)
import tkinter as tk
from tkinter import messagebox

from controllers import AuthController


class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = AuthController()
        self.configure(bg='#ffffff')
        self._create_widgets()

    def _create_widgets(self):
        container = tk.Frame(self, bg='#ffffff')
        container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(container, text="Gestion de Parc Automobile", font=('Helvetica', 20, 'bold'), bg='#ffffff', fg='#000000').pack(pady=(0, 10))
        tk.Label(container, text="Connexion", font=('Helvetica', 14), bg='#ffffff', fg='#333333').pack(pady=(5, 30))

        form = tk.Frame(container, bg='#f5f5f5', padx=40, pady=30)
        form.pack()

        tk.Label(form, text="Nom d'utilisateur", font=('Helvetica', 10), bg='#f5f5f5', fg='#333333').pack(anchor='w')
        self.username_var = tk.StringVar()
        tk.Entry(form, textvariable=self.username_var, font=('Helvetica', 12), width=25,
                bg='#ffffff', fg='#000000', insertbackground='#000000').pack(pady=(5, 15))

        tk.Label(form, text="Mot de passe", font=('Helvetica', 10), bg='#f5f5f5', fg='#333333').pack(anchor='w')
        self.password_var = tk.StringVar()
        pwd_entry = tk.Entry(form, textvariable=self.password_var, font=('Helvetica', 12), width=25, show='*',
                            bg='#ffffff', fg='#000000', insertbackground='#000000')
        pwd_entry.pack(pady=(5, 20))
        pwd_entry.bind('<Return>', lambda e: self._login())

        tk.Button(form, text="Se connecter", command=self._login, bg='#3498db', fg='#000000',
                 font=('Helvetica', 11, 'bold'), relief='flat', width=20, pady=8, cursor='hand2').pack()

        quit_btn = tk.Button(form, text="Quitter", bg='#d0d0d0', fg='#000000',
                 font=('Helvetica', 10), relief='flat', width=20, pady=5, cursor='hand2')
        quit_btn.config(command=self.app.quit_app)
        quit_btn.pack(pady=(10, 0))

        tk.Label(container, text="admin / admin123", font=('Helvetica', 9), bg='#ffffff', fg='#666666').pack(pady=(20, 0))
    
    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        result = self.controller.login(username, password)
        if result.success:
            self.app.on_login_success(result.data)
        else:
            messagebox.showerror("Erreur", result.message)
            self.password_var.set("")
