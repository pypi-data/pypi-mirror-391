from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator

# Define standard fields as a module-level constant
STANDARD_FIELDS = {
    "$submissionId",
    "$owner",
    "$status",
    "$lastUpdatedAt",
    "$lastModifiedAt",
    "$createdAt",
    "$updatedAt",
    "$state",
}


class FilterCondition(BaseModel):
    operator: Literal[
        "CONTAINS",
        "NOT_IN",
        "EQ",
        "NEQ",
        "EMPTY",
        "NON_EMPTY",
        "STARTS_WITH",
        "BETWEEN",
        "GT",
        "LT",
        "GTE",
        "LTE",
        "ENDS_WITH",
    ] = Field(
        description="Filter operator to apply, possible values are CONTAINS, NOT_IN, EQ, NEQ, EMPTY, NON_EMPTY, STARTS_WITH, BETWEEN, GT, LT, GTE, LTE, ENDS_WITH",
    )
    filter_key_type: Literal["STANDARD", "CUSTOM"] = Field(
        description="Type of field being filtered, possible values are STANDARD, CUSTOM",
    )
    key: str = Field(
        min_length=1,
        description="Field key to filter on, use $submissionId, $owner, $status, $lastUpdatedAt, $lastModifiedAt, $createdAt, $updatedAt, $state for standard fields or the field name for custom fields",
    )
    value: Any = Field(description="Value to filter by")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str, info: ValidationInfo) -> str:
        filter_key_type = info.data.get("filter_key_type")
        if filter_key_type == "STANDARD":
            if v not in STANDARD_FIELDS:
                raise ValueError(
                    f"Standard filterKeyType used but key '{v}' is not a standard field. "
                    f"Valid standard fields are: {', '.join(sorted(STANDARD_FIELDS))}"
                )
        return v

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> FilterCondition:
        """Create FilterCondition from JSON data"""
        # Validate and extract required fields
        key = json_data.get("key")
        if not key or not isinstance(key, str):
            raise ValueError(
                "Parameter 'key' must be present and be a non-empty string"
            )

        operator = json_data.get("operator", "EQ")
        if not isinstance(operator, str):
            operator = "EQ"

        filter_key_type = json_data.get("filterKeyType", "CUSTOM")
        if not isinstance(filter_key_type, str):
            filter_key_type = "CUSTOM"

        return cls(
            operator=operator,  # type: ignore[arg-type]
            filter_key_type=filter_key_type,  # type: ignore[arg-type]
            key=key,
            value=json_data.get("value"),
        )

    def assign_from_json(self, json_data: dict[str, Any] | None) -> None:
        """In-place assignment from JSON"""
        if not json_data:
            return

        if "operator" in json_data and isinstance(json_data["operator"], str):
            self.operator = json_data["operator"]  # type: ignore[assignment]
        if "filterKeyType" in json_data and isinstance(json_data["filterKeyType"], str):
            self.filter_key_type = json_data["filterKeyType"]  # type: ignore[assignment]
        if "key" in json_data and isinstance(json_data["key"], str):
            self.key = json_data["key"]
        if "value" in json_data:
            self.value = json_data["value"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "operator": self.operator,
            "filterKeyType": self.filter_key_type,
            "key": self.key,
            "value": self.value,
        }


class SubmissionQuery(BaseModel):
    queries: list[SubmissionQuery] = Field(
        default_factory=list, description="Array of nested queries"
    )
    conditions: list[FilterCondition] = Field(
        default_factory=list, description="Array of filter conditions"
    )
    operator: Literal["AND", "OR"] = Field(
        default="AND", description="Logical operator, possible values are AND, OR"
    )

    @model_validator(mode="after")
    def validate_queries_or_conditions(self) -> SubmissionQuery:
        """Ensure at least one of queries or conditions is provided"""
        if not self.queries and not self.conditions:
            raise ValueError("Either queries or conditions must be provided")
        return self

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> SubmissionQuery:
        """Create SubmissionQuery from JSON data"""
        if not json_data:
            return cls()

        operator = json_data.get("operator", "AND")
        if not isinstance(operator, str) or operator not in ["AND", "OR"]:
            operator = "AND"

        query = cls(operator=operator)  # type: ignore[arg-type]

        # Handle nested queries
        if json_data.get("queries") and isinstance(json_data["queries"], list):
            query.queries = [
                cls.from_json(q) for q in json_data["queries"] if isinstance(q, dict)
            ]

        # Handle conditions
        if json_data.get("conditions") and isinstance(json_data["conditions"], list):
            query.conditions = [
                FilterCondition.from_json(c)
                for c in json_data["conditions"]
                if isinstance(c, dict)
            ]

        return query

    def assign_from_json(self, json_data: dict[str, Any] | None) -> None:
        """In-place assignment from JSON (matches JavaScript method signature)"""
        if not json_data:
            return

        # Handle operator
        if "operator" in json_data and isinstance(json_data["operator"], str):
            if json_data["operator"] in ["AND", "OR"]:
                self.operator = json_data["operator"]  # type: ignore[assignment]

        # Handle nested queries
        if json_data.get("queries") and isinstance(json_data["queries"], list):
            self.queries = []
            for q in json_data["queries"]:
                if isinstance(q, dict):
                    query = SubmissionQuery()
                    query.assign_from_json(q)
                    self.queries.append(query)

        # Handle conditions
        if json_data.get("conditions") and isinstance(json_data["conditions"], list):
            self.conditions = []
            for c in json_data["conditions"]:
                if isinstance(c, dict):
                    try:
                        condition = FilterCondition.from_json(c)
                        self.conditions.append(condition)
                    except (ValueError, TypeError):
                        # Skip invalid conditions
                        continue

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result: dict[str, Any] = {"operator": self.operator}

        if self.queries:
            result["queries"] = [query.to_dict() for query in self.queries]

        if self.conditions:
            result["conditions"] = [
                condition.to_dict() for condition in self.conditions
            ]

        return result


class AggregationOperand(BaseModel):
    field_name: str = Field(description="Name of the field to aggregate")
    label: str = Field(description="Display label for the operand")
    data_type: str = Field(
        description="Data type of the operand field, use text, number, date, boolean, select for standard fields or the field type for custom fields"
    )
    dimension_type: Literal["STANDARD", "CUSTOM"] = Field(
        default="CUSTOM",
        description="Type of operand field, possible values are STANDARD, CUSTOM",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "fieldName": self.field_name,
            "label": self.label,
            "dataType": self.data_type,
            "dimensionType": self.dimension_type,
        }


class AggregationDimension(BaseModel):
    field_name: str = Field(description="Name of the field to group by")
    label: str = Field(description="Display label for the dimension")
    data_type: str = Field(
        description="Data type of the field, use text, number, date, boolean, select for standard fields or the field type for custom fields"
    )
    dimension_type: Literal["STANDARD", "CUSTOM"] = Field(
        default="CUSTOM",
        description="Type of dimension field, possible values are STANDARD, CUSTOM",
    )
    sort_direction: Literal["asc", "desc"] | None = Field(
        None, description="Sort direction, possible values are asc, desc"
    )
    sort_type: Literal["number", "string"] | None = Field(
        None, description="Type of sorting, possible values are number, string"
    )
    missing_value: str | None = Field(
        None, description="Value when field data is missing"
    )
    interval: Literal["day", "week", "month", "year"] | None = Field(
        None, description="Interval for date/time grouping, use day, week, month, year"
    )

    def to_dict(self) -> dict[str, Any]:
        result = {
            "fieldName": self.field_name,
            "label": self.label,
            "dataType": self.data_type,
            "dimensionType": self.dimension_type,
        }
        if self.sort_direction:
            result["sortDirection"] = self.sort_direction
        if self.sort_type:
            result["sortType"] = self.sort_type
        if self.missing_value is not None:
            result["missingValue"] = self.missing_value
        if self.interval:
            result["interval"] = self.interval
        return result


class AggregationMetric(BaseModel):
    type: Literal["count", "sum", "average", "minimum", "maximum", "unique"] = Field(
        default="count",
        description="Type of aggregation, possible values are count, sum, average, minimum, maximum, unique",
    )
    operand: AggregationOperand | None = Field(
        default=None, description="Field to aggregate"
    )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"type": self.type}
        if self.operand:
            result["operand"] = self.operand.to_dict()
        return result
