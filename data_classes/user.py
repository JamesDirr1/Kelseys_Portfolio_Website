from dataclasses import dataclass
from typing import Optional
from datetime import date
from werkzeug.security import generate_password_hash
#Data class that represents the columns from the category table.

@dataclass
class User:
    user_id: int
    user_name: str
    user_password: str
    user_created_date: Optional[date] = None
