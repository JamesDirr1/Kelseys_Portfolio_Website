import data_classes
from typing import Optional

#Data class that represents the columns from the category table.

@data_classes
class category:
    category_id: Optional[int] = None
    category_title: str
    category_order: Optional[int] = None


