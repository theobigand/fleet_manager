from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Log:
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: Optional[str] = None
    date_action: Optional[str] = None
    details: Optional[str] = None
    username: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Log":
        if not data:
            return None
        filtered_data = {}
        for k, v in data.items():
            if k in cls.__dataclass_fields__:
                filtered_data[k] = v
        return cls(**filtered_data)
    
    def to_dict(self) -> dict:
        return asdict(self)
