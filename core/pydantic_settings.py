from pydantic_settings import BaseSettings
from typing import Optional
import os


class PydanticSettings(BaseSettings):
    """
    Pydantic settings configuration for the project
    """
    
    # API Settings
    API_TITLE: str = "Coveme API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for marketplace integration and analytics"
    
    # Validation Settings
    STRICT_VALIDATION: bool = True
    ALLOW_EXTRA_FIELDS: bool = False
    VALIDATE_ASSIGNMENT: bool = True
    
    # Serialization Settings
    SERIALIZE_EXCLUDE_NONE: bool = True
    SERIALIZE_EXCLUDE_UNSET: bool = True
    
    # Error Handling
    SHOW_ERROR_DETAILS: bool = True
    LOG_VALIDATION_ERRORS: bool = True
    
    # Performance Settings
    CACHE_SCHEMAS: bool = True
    MAX_VALIDATION_ERRORS: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
pydantic_settings = PydanticSettings()


def get_pydantic_config():
    """
    Get Pydantic configuration dictionary
    """
    return {
        "strict": pydantic_settings.STRICT_VALIDATION,
        "extra": "forbid" if not pydantic_settings.ALLOW_EXTRA_FIELDS else "ignore",
        "validate_assignment": pydantic_settings.VALIDATE_ASSIGNMENT,
        "ser_json_timedelta": "iso8601",
        "ser_json_bytes": "base64",
        "ser_json_inf_nan": "null",
        "ser_json_exclude_none": pydantic_settings.SERIALIZE_EXCLUDE_NONE,
        "ser_json_exclude_unset": pydantic_settings.SERIALIZE_EXCLUDE_UNSET,
    }
