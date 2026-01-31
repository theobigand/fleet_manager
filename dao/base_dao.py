import sqlite3
import os
from typing import Optional, List, Dict, Any, Type, TypeVar
from config import DB_PATH

T = TypeVar('T')

class BaseDAO:    
    _schema_initialized = False
    
    @staticmethod
    def get_connection() -> sqlite3.Connection:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @classmethod
    def init_schema(cls) -> None:
        if cls._schema_initialized:
            return
        
        sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'create_table.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = cls.get_connection()
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        cls._schema_initialized = True
    
    def __init__(self):
        self.init_schema()
    
    def _execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.get_connection()
        cursor = conn.execute(query, params)
        conn.commit()
        conn.close()
        return cursor
    
    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute(query, params).fetchone()
        conn.close()
        return dict(row) if row else None
    
    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def _insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        filtered = {k: v for k, v in data.items() if v is not None}
        columns = ", ".join(filtered.keys())
        placeholders = ", ".join("?" * len(filtered))
        
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                list(filtered.values())
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def _update(self, table: str, id: int, data: Dict[str, Any]) -> None:
        if not data:
            return
        sets = ", ".join(f"{k} = ?" for k in data.keys())
        values = list(data.values()) + [id]
        
        conn = self.get_connection()
        conn.execute(f"UPDATE {table} SET {sets} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    def _delete(self, table: str, id: int) -> None:
        conn = self.get_connection()
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        conn.commit()
        conn.close()
