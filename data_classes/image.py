import data_classes
from typing import Optional
from datetime import date

#Data class that represents the columns from the image table.

@data_classes
class image:
    image_id: Optional[int] = None
    image_title: Optional[str] = None
    image_desc: Optional[str] = None
    image_url: str
    image_weight: int
    project_id: int