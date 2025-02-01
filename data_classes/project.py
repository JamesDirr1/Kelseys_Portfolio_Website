from dataclasses import dataclass
from typing import Optional
from datetime import date

#Data class that represents the columns from the project table.


@dataclass
class project:
    project_title: str
    project_date: date = date.today()
    project_image_url: str = "https://static.wixstatic.com/media/0fee66_18f00ad0221142dfbd4c21f7e54d425f~mv2.png/v1/fill/w_549,h_289,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Kelsey_Spade_Header.png"
    project_image_id: Optional[int] = None
    project_id: Optional[int] = None
    project_desc: Optional[str] = None
    category_id: Optional[int] = None