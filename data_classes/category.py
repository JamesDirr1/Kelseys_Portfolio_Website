from dataclasses import dataclass
from typing import Optional

#Data class that represents the columns from the category table.

@dataclass
class category:
    category_title: str
    category_id: Optional[int] = None
    category_order: Optional[int] = None


