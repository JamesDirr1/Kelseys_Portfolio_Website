from dataclasses import dataclass
from typing import Any, Dict, Optional

import utility_classes.custom_logger

# Data class that represents the columns from the category table.


@dataclass
class Category:
    category_title: str
    category_id: Optional[int] = None
    category_order: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        logger = utility_classes.custom_logger.log("DATA")
        logger.debug(f"Attempting to create Category: {data}")
        try:
            category = cls(
                category_id=int(data["category_id"]),
                category_title=str(data["category_title"]),
                category_order=int(data["category_order"]),
            )
            logger.debug(f"Successfully created Category: {category}")
            return category
        except KeyError as e:
            logger.error(
                f"Missing expected key: {e} in data: {data} when creating Category"
            )
            raise KeyError(
                f"Missing expected key: {e} in data: {data} when creating Category"
            )
        except (TypeError, ValueError) as e:
            logger.error(
                f"Invalid value type when creating Category: {e}, data: {data}"
            )
            raise type(e)(
                f"Invalid value type when creating Category: {e}, data: {data}"
            )
        except Exception as e:
            logger.error(f"Unexpected error when creating Category: {e}, data: {data}")
            raise Exception(
                f"Unexpected error when creating Category: {e}, data: {data}"
            )
