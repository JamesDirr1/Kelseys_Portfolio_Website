from dataclasses import dataclass
from typing import Any, Dict, Optional

import utility_classes.custom_logger

# Data class that represents the columns from the image table.


@dataclass
class Image:
    image_weight: int
    project_id: int
    image_id: Optional[int] = None
    image_title: Optional[str] = None
    image_desc: Optional[str] = None
    image_url: str = (
        "https://static.wixstatic.com/media/0fee66_18f00ad0221142dfbd4c21f7e54d425f~mv2.png/v1/fill/w_549,h_289,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Kelsey_Spade_Header.png"
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Image":
        logger = utility_classes.custom_logger.log("DATA")
        logger.debug(f"Attempting to create Image: {data}")
        try:
            image = cls(
                image_id=int(data["image_id"]),
                image_title=str(data["image_title"]),
                image_desc=str(data["image_desc"]),
                image_url=str(data["image_URL"]),
                image_weight=int(data["image_weight"]),
                project_id=int(data["project_id"]),
            )
            logger.debug(f"Successfully created Image: {image}")
            return image
        except KeyError as e:
            logger.error(
                f"Missing expected key: {e} in data: {data} when creating Image"
            )
            raise KeyError(
                f"Missing expected key: {e} in data: {data} when creating Image"
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid value type when creating Image: {e}, data: {data}")
            raise type(e)(f"Invalid value type when creating Image: {e}, data: {data}")
        except Exception as e:
            logger.error(f"Unexpected error when creating Image: {e}, data: {data}")
            raise Exception(f"Unexpected error when creating Image: {e}, data: {data}")

    @classmethod
    def from_project_dict(cls, data: Dict[str, Any]) -> "Image":
        logger = utility_classes.custom_logger.log("DATA")
        logger.debug(f"Attempting to create Image from Project data: {data}")
        try:
            if data.get("project_image_id") is None:
                logger.debug("Creating 'Null' project image with weight 0")
                return cls(project_id=int(data["project_id"]), image_weight=0)

            image = cls(
                image_id=int(data["project_image_id"]),
                image_title=str(data.get("image_title")),
                image_desc=str(data.get("image_desc")),
                image_url=str(data.get("image_URL")),
                image_weight=int(data.get("image_weight", 0)),
                project_id=int(data["project_id"]),
            )
            logger.debug(f"Successfully created Image from Project data: {image}")
            return image

        except KeyError as e:
            logger.error(
                f"Missing expected key: {e} in data: {data} when creating Image from project"
            )
            raise KeyError(
                f"Missing expected key: {e} in data: {data} when creating Image from project"
            )
        except (TypeError, ValueError) as e:
            logger.error(
                f"Invalid value type when creating Image from project: {e}, data: {data}"
            )
            raise type(e)(
                f"Invalid value type when creating Image from project: {e}, data: {data}"
            )
        except Exception as e:
            logger.error(
                f"Unexpected error when creating Image from project: {e}, data: {data}"
            )
            raise Exception(
                f"Unexpected error when creating Image from project: {e}, data: {data}"
            )
