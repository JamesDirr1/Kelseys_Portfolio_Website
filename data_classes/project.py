import data_classes
from typing import Optional
from datetime import date

#Data class that represents the columns from the project table.


@data_classes
class project:
    project_id: Optional[int] = None
    project_title: str
    project_date: date = date.today()
    project_desc: Optional[str] = None
    project_image_id: Optional[int] = None
    category_id: Optional[int] = None