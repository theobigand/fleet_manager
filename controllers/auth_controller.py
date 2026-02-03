from typing import Optional, List
from models import User, Log
from dao import UserDAO
from controllers.result import Result


class AuthController:
    
    def __init__(self) -> None:
        self.dao = UserDAO()
    
    def login(self, username: str, password: str) -> Result:
        if not username or not password:
            return Result.error("Identifiants requis")
        
        user = self.dao.find_by_credentials(username, password)
        if user:
            self.dao.add_log(user.id, 'CONNEXION', f"Connexion de {username}")
            return Result.ok(user, "Connexion réussie")
        return Result.error("Identifiants invalides")
    
    def logout(self, user_id: int) -> None:
        self.dao.add_log(user_id, 'DECONNEXION', "Déconnexion")
    
    def create_user(self, data: dict, password: str, admin_user_id: int) -> Result:
        username = data.get('username', '').strip()
        if not username:
            return Result.error("Nom d'utilisateur obligatoire")
        if not password:
            return Result.error("Mot de passe obligatoire")
        
        if self.dao.find_by_username(username):
            return Result.error("Ce nom d'utilisateur existe déjà")
        
        user = User(
            username=username,
            role=data.get('role', 'employe'),
            nom=data.get('nom'),
            prenom=data.get('prenom'),
            email=data.get('email')
        )
        
        user_id = self.dao.create(user, password)
        if user_id:
            self.dao.add_log(admin_user_id, 'CREATION_UTILISATEUR', f"Création de {username}")
            return Result.ok(user_id, "Utilisateur créé")
        return Result.error("Erreur lors de la création")
    
    def get_all_users(self) -> List[User]:
        return self.dao.find_all()

    def delete_user(self, username: str, admin_user_id: int) -> Result:
        user = self.dao.find_by_username(username)
        if not user:
            return Result.error("Utilisateur non trouvé")

        if user.id == admin_user_id:
            return Result.error("Vous ne pouvez pas supprimer votre propre compte")

        self.dao._update('users', user.id, {'actif': 0})
        self.dao.add_log(admin_user_id, 'DESACTIVATION_UTILISATEUR', f"Désactivation de {username}")
        return Result.ok(None, "Utilisateur désactivé")

    def get_logs(self, limit: int = 100) -> List[Log]:
        return self.dao.get_logs(limit)

    def init_default_admin(self) -> None:
        self.dao.create_default_admin()
