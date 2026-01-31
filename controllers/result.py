from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    """Résultat d'une opération"""
    success: bool
    message: str = ""
    data: Any = None
    
    @classmethod
    def ok(cls, data: Any = None, message: str = "") -> "Result":
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error(cls, message: str) -> "Result":
        return cls(success=False, message=message)