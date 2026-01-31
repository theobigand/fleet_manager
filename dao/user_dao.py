# dao/user_dao.py - Accès aux données des utilisateurs et logs
import hashlib
from typing import Optional, List
from dao.base_dao import BaseDAO
from models import User, Log


class UserDAO(BaseDAO):
    """DAO pour les utilisateurs et logs"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def find_by_credentials(self, username: str, password: str) -> Optional[User]:
        row = self._fetch_one(
            "SELECT * FROM users WHERE username = ? AND password_hash = ? AND actif = 1",
            (username, self.hash_password(password))
        )
        return User.from_dict(row)
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        row = self._fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return User.from_dict(row)
    
    def find_by_username(self, username: str) -> Optional[User]:
        row = self._fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        return User.from_dict(row)
    
    def find_all(self) -> List[User]:
        rows = self._fetch_all("SELECT * FROM users ORDER BY nom, prenom")
        return [User.from_dict(row) for row in rows]
    
    def create(self, user: User, password: str) -> Optional[int]:
        data = user.to_dict()
        data.pop('id', None)
        data['password_hash'] = self.hash_password(password)
        return self._insert('users', data)
    
    def create_default_admin(self) -> None:
        if not self.find_by_username('admin'):
            admin = User(username='admin', role='admin', nom='Administrateur', prenom='Système')
            self.create(admin, 'admin123')
    
    # === LOGS ===
    def add_log(self, user_id: Optional[int], action: str, details: str = "") -> None:
        self._insert('logs', {'user_id': user_id, 'action': action, 'details': details})
    
    def get_logs(self, limit: int = 100) -> List[Log]:
        rows = self._fetch_all("""
            SELECT l.*, u.username 
            FROM logs l LEFT JOIN users u ON l.user_id = u.id 
            ORDER BY l.date_action DESC LIMIT ?
        """, (limit,))
        return [Log.from_dict(row) for row in rows]
