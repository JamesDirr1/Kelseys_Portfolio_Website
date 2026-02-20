from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from utility_classes.custom_logger import log
from data_classes.image import Image

# Data class that represents the columns from the project table.


@dataclass
class Project:
    project_title: str
    project_image: Optional[Image] = None
    project_image_id: Optional[int] = None
    project_date: date = date.today()
    project_id: Optional[int] = None
    project_desc: Optional[str] = None
    category_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        logger = log("DATA")
        logger.debug(f"Attempting to create Project: {data}")
        try:
            # Handle optional image creation
            project_image = None
            if "image_URL" in data:  # Only create Image if related data exists
                project_image = Image.from_project_dict(data)

            project = cls(
                project_title=str(data["project_title"]),
                project_date=str(data["project_date"]),
                project_desc=str(data["project_desc"]),
                project_id=int(data["project_id"]),
                project_image_id=(
                    int(data["project_image_id"])
                    if data.get("project_image_id")
                    else None
                ),
                category_id=int(data["category_id"]),
                project_image=project_image,
            )

            logger.debug(f"Successfully created Project: {project}")
            return project

        except KeyError as e:
            logger.error(
                f"Missing expected key: {e} in data: {data} when creating Project"
            )
            raise KeyError(
                f"Missing expected key: {e} in data: {data} when creating Project"
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid value type when creating Project: {e}, data: {data}")
            raise type(e)(
                f"Invalid value type when creating Project: {e}, data: {data}"
            )
        except Exception as e:
            logger.error(f"Unexpected error when creating Project: {e}, data: {data}")
            raise Exception(
                f"Unexpected error when creating Project: {e}, data: {data}"
            )
