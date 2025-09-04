from dataclasses import dataclass
from typing import Optional, Any, Dict
from datetime import date
from werkzeug.security import generate_password_hash
import utility_classes.custom_logger

# Data class that represents the columns from the category table.


@dataclass
class User:
    user_id: int
    user_name: str
    user_password: str
    user_created_date: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        logger = utility_classes.custom_logger.log("DATA")
        logger.debug("Attempting to create User")
        try:
            user = cls(
                user_id=int(data["user_id"]),
                user_name=str(data["user_name"]),
                user_password=str(data["user_password"]),
            )
            logger.debug(f"Successfully created user: {user.user_name}")
            return user

        except KeyError as e:
            logger.error(f"Missing expected key: {e} in data when creating user")
            raise KeyError(f"Missing expected key: {e} in data when creating user")
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid value type when creating user: {e}")
            raise type(e)(f"Invalid value type when creating user: {e}")
        except Exception as e:
            logger.error(f"Unexpected error when creating user: {e}")
            raise Exception(f"Unexpected error when creating user: {e}")
