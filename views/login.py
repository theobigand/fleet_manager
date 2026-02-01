import customtkinter as ctk
from tkinter import messagebox
from controllers import AuthController


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent)
        self.app = app
        self.controller = AuthController()
        self.setup_login()

    def setup_login(self) -> None:
        # titre principal
        titre = ctk.CTkLabel(self, text="Gestion de Parc Automobile", font=ctk.CTkFont(size=24, weight='bold'))
        titre.pack(pady=30)

        # connexion
        sous_titre = ctk.CTkLabel(self, text="Connexion", font=ctk.CTkFont(size=18))
        sous_titre.pack(pady=10)

        # frame pour le formulaire
        form_frame = ctk.CTkFrame(self, fg_color='transparent')
        form_frame.pack(pady=20, padx=30)

        # username
        label_user = ctk.CTkLabel(form_frame, text="Nom d'utilisateur:")
        label_user.grid(row=0, column=0, sticky='w', pady=5, padx=20)
        self.username_var = ctk.StringVar()
        entry_user = ctk.CTkEntry(form_frame, textvariable=self.username_var, width=250)
        entry_user.grid(row=1, column=0, pady=5, padx=20)

        # password
        label_pass = ctk.CTkLabel(form_frame, text="Mot de passe:")
        label_pass.grid(row=2, column=0, sticky='w', pady=(15, 5), padx=20)
        self.password_var = ctk.StringVar()
        entry_pass = ctk.CTkEntry(form_frame, textvariable=self.password_var, width=250, show='*')
        entry_pass.grid(row=3, column=0, pady=5, padx=20)
        entry_pass.bind('<Return>', lambda e: self.login())

        # boutons
        # login
        btn_login = ctk.CTkButton(form_frame, text="Se connecter", command=self.login,
                                   fg_color='#4CAF50', hover_color='#45a049', width=200)
        btn_login.grid(row=4, column=0, pady=20, padx=20)

        # quit
        btn_quit = ctk.CTkButton(form_frame, text="Quitter", command=self.app.quit_app,
                                  fg_color='#6c757d', hover_color='#5a6268', width=200)
        btn_quit.grid(row=5, column=0, pady=(0, 20), padx=20)

        info = ctk.CTkLabel(self, text="Compte test: admin / admin123", text_color='gray')
        info.pack(pady=10)

    def login(self) -> None:
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