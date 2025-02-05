from dataclasses import dataclass
from typing import Optional
from datetime import date
from data_classes.image import Image

#Data class that represents the columns from the project table.


@dataclass
class Project:
    project_title: str
    project_image: Optional[Image] = None
    project_image_id: Optional[int] = None
    project_date: date = date.today()
    project_id: Optional[int] = None
    project_desc: Optional[str] = None
    category_id: Optional[int] = None