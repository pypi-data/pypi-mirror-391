import json
import re
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...json_serialized import JsonSerializableMixin


class ValidatedString(str):
    """Custom string type with common validation patterns"""

    @classmethod
    def field_name_validator(cls, v: str | None) -> str | None:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Field name cannot be empty")
            v = v.strip()
            if not re.match(r"^[_a-z][\d_a-z]*$", v):
                raise ValueError(
                    "Field name must start with letter/underscore and contain only lowercase letters, numbers, underscore"
                )
        return v

    @classmethod
    def non_empty_string_validator(
        cls, v: str | None, field_name: str = "Field"
    ) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError(f"{field_name} cannot be empty")
        return v.strip() if v else v

    @classmethod
    def url_validator(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL is required")
        v = v.strip()
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Must be a valid URL")
        except Exception as err:
            raise ValueError("Must be a valid URL") from err
        return v

    @classmethod
    def json_string_validator(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError as err:
                raise ValueError("Must be valid JSON string") from err
        return v


class UniqueListValidator:
    """Validator for ensuring list uniqueness"""

    @classmethod
    def validate_unique_strings(
        cls, v: list[str] | None, field_name: str = "Items"
    ) -> list[str] | None:
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError(f"{field_name} must be unique")
            for item in v:
                if not item or not item.strip():
                    raise ValueError(f"{field_name} cannot contain empty values")
        return v


class BaseFieldComponent(BaseModel, JsonSerializableMixin):
    """Base component for field-related models"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


class BaseUpsertFieldRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    label: str = Field(description="Display label for the field")
    new_field_name: str | None = Field(
        None,
        description="New field variable name for the field, mandatory if field name needs to be changed",
    )
    description: str | None = Field(
        None,
        description="Field description, Example: This is a description for the field",
    )
    placeholder: str | None = Field(default=None, description="Field placeholder")
    dependency_app_id: str | None = Field(
        None, description="Dependency app ID, must be a valid Clappia app ID"
    )
    server_url: str | None = Field(
        None, description="Server URL, mandatory if field type is getDataFromRestApis"
    )
    display_condition: str | None = Field(
        None, description="Display condition Example: {field_name} == 'value'"
    )
    required: bool = Field(default=False, description="Whether field is required")
    hidden: bool = Field(default=False, description="Whether field is hidden")
    is_editable: bool = Field(default=True, description="Whether field is editable")
    editability_condition: str | None = Field(
        None, description="Editability condition, Example: {field_name} == 'value'"
    )
    default_value: str | None = Field(
        None, description="Default value, Example: 'value'"
    )
    block_width_percentage_desktop: int = Field(default=50, description="Desktop width")
    block_width_percentage_mobile: int = Field(default=100, description="Mobile width")
    retain_values: bool = Field(default=True, description="Retain values when hidden")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str | None:
        return ValidatedString.non_empty_string_validator(v, "Label")


class BaseUpsertPageRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    app_id: str = Field(description="App ID")
    version_variable_name: str | None = Field(
        None,
        description="The variable name representing the app version. If not specified, the live version is used",
    )

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str | None:
        return ValidatedString.non_empty_string_validator(v, "App ID")


class BaseUpsertSectionRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    app_id: str = Field(description="App ID")
    version_variable_name: str | None = Field(
        None,
        description="The variable name representing the app version. If not specified, the live version is used",
    )
    section_index: int = Field(ge=0, description="Section index")
    page_index: int = Field(ge=0, description="Page index")

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str | None:
        return ValidatedString.non_empty_string_validator(v, "App ID")
