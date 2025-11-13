from pydantic import BaseModel, ConfigDict, Field

from ...json_serialized import JsonSerializableMixin
from .model import ExternalFilter


class BaseFieldComponent(BaseModel, JsonSerializableMixin):
    """Base component for field-related models"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


class ValidatedString(str):
    """Custom string type with common validation patterns"""

    @classmethod
    def non_empty_string_validator(
        cls, v: str | None, field_name: str = "Field"
    ) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError(f"{field_name} cannot be empty")
        return v.strip() if v else v

    @classmethod
    def number_validator(cls, v: int | None, field_name: str = "Field") -> int | None:
        if v is not None:
            raise ValueError(f"{field_name} cannot be empty")
        return v


class BaseUpsertChartRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    width: int = Field(default=50, description="Width of the chart")
    filters: list[ExternalFilter] | None = Field(
        default=None, description="Filters for the chart"
    )
