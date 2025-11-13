from abc import ABC
from typing import Any, Literal

from pydantic import BaseModel

from clappia_api_tools.models.request import (
    CreateSubmissionRequest,
    EditSubmissionRequest,
    GetSubmissionsAggregationRequest,
    GetSubmissionsCountRequest,
    GetSubmissionsInExcelRequest,
    GetSubmissionsRequest,
    UpdateSubmissionOwnersRequest,
    UpdateSubmissionStatusRequest,
)
from clappia_api_tools.models.submission import (
    AggregationDimension,
    AggregationMetric,
    SubmissionQuery,
)

from .base_client import BaseAPIKeyClient, BaseAuthTokenClient, BaseClappiaClient


class ClientResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


class SubmissionClient(BaseClappiaClient, ABC):
    """Client for managing Clappia submissions.

    This client handles retrieving and managing submissions, including
    getting submissions, getting submissions aggregation, creating submissions,
    editing submissions, updating submission status, updating submission owners.
    """

    def get_submissions(
        self,
        app_id: str,
        fields: list[str] | None = None,
        page_size: int = 10,
        forward: bool = True,
        filters: SubmissionQuery | None = None,
        last_submission_id: str | None = None,
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = GetSubmissionsRequest(
                app_id=app_id,
                page_size=page_size,
                forward=forward,
                filters=filters,
                last_submission_id=last_submission_id,
                fields=fields,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "pageSize": request.page_size,
            "forward": request.forward,
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/getSubmissions", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )
        return ClientResponse(
            success=True,
            data=response_data
        )

    def get_submissions_aggregation(
        self,
        app_id: str,
        dimensions: list[AggregationDimension] | None = None,
        aggregation_dimensions: list[AggregationMetric] | None = None,
        x_axis_labels: list[str] | None = None,
        forward: bool = True,
        page_size: int = 1000,
        filters: SubmissionQuery | None = None,
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = GetSubmissionsAggregationRequest(
                app_id=app_id,
                dimensions=dimensions,
                aggregation_dimensions=aggregation_dimensions,
                x_axis_labels=x_axis_labels,
                forward=forward,
                page_size=page_size,
                filters=filters,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        if not request.dimensions and not request.aggregation_dimensions:
            return ClientResponse(
                success=False,
                error="At least one dimension or aggregation dimension must be provided"
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "forward": request.forward,
            "pageSize": request.page_size,
            "xAxisLabels": request.x_axis_labels or [],
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }

        if request.dimensions:
            payload["dimensions"] = [dim.to_dict() for dim in request.dimensions]
        if request.aggregation_dimensions:
            payload["aggregationDimensions"] = [
                agg.to_dict() for agg in request.aggregation_dimensions
            ]
        if request.filters:
            payload["filters"] = request.filters.to_dict()


        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="submissions/getSubmissionsAggregation",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )

        return ClientResponse(
            success=True,
            data=response_data
        )

    def create_submission(
        self,
        app_id: str,
        data: dict[str, Any],
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = CreateSubmissionRequest(
                app_id=app_id,
                data=data,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        if not data:
            return ClientResponse(
                success=False,
                error="data cannot be empty - at least one field is required"
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "data": request.data,
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/create", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )


        return ClientResponse(
            success=True,
            data=response_data
        )

    def edit_submission(
        self,
        app_id: str,
        submission_id: str,
        data: dict[str, Any],
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = EditSubmissionRequest(
                app_id=app_id,
                submission_id=submission_id,
                data=data,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        if not data:
            return ClientResponse(
                success=False,
                error="data cannot be empty - at least one field is required"
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "submissionId": request.submission_id,
            "data": request.data,
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/edit", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )

        return ClientResponse(
            success=True,
            data=response_data
        )

    def update_status(
        self,
        app_id: str,
        submission_id: str,
        status_name: str,
        comments: str | None = None,
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = UpdateSubmissionStatusRequest(
                app_id=app_id,
                submission_id=submission_id,
                status_name=status_name,
                comments=comments,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        status: dict[str, Any] = {
            "name": request.status_name.strip(),
            "comments": request.comments.strip() if request.comments else None,
        }

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "submissionId": request.submission_id,
            "status": status,
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/updateStatus", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )

        return ClientResponse(
            success=True,
            data=response_data
        )

    def update_owners(
        self,
        app_id: str,
        submission_id: str,
        email_ids: list[str],
        phone_numbers: list[str] | None = None,
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = UpdateSubmissionOwnersRequest(
                app_id=app_id,
                submission_id=submission_id,
                email_ids=email_ids,
                phone_numbers=phone_numbers,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "submissionId": request.submission_id,
            "emailIds": [str(email) for email in request.email_ids],
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/updateSubmissionOwners", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )

        return ClientResponse(
            success=True,
            data=response_data
        )

    def get_submissions_in_excel(
        self,
        app_id: str,
        requesting_user_email_address: str,
        filters: SubmissionQuery | None = None,
        field_names: list[str] | None = None,
        format: Literal["Excel", "Csv"] = "Excel",
    ) -> ClientResponse:
        try:
            request = GetSubmissionsInExcelRequest(
                app_id=app_id,
                requesting_user_email_address=requesting_user_email_address,
                filters=filters,
                field_names=field_names,
                format=format,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "requestingUserEmailAddress": str(request.requesting_user_email_address),
            "format": request.format,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()
        if request.field_names:
            payload["fieldNames"] = request.field_names


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/getSubmissionsExcel", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )

        if response_data and response_data.get("statusCode") == 202:
            return ClientResponse(
                success=True,
                data=response_data
            )
        else:
            return ClientResponse(
                success=True,
                data=response_data
            )

    def get_submissions_count(
        self,
        app_id: str,
        filters: SubmissionQuery | None = None,
        requesting_user_email_address: str | None = None,
    ) -> ClientResponse:
        try:
            request = GetSubmissionsCountRequest(
                app_id=app_id,
                filters=filters,
                requesting_user_email_address=requesting_user_email_address,
            )
        except Exception as e:
            return ClientResponse(
                success=False,
                error=str(e)
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(
                success=False,
                error=env_error
            )

        payload: dict[str, Any] = {
            "appId": request.app_id,
            "requestingUserEmailAddress": request.requesting_user_email_address,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()


        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/getSubmissionsCount", data=payload
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message
            )

        return ClientResponse(
            success=True,
            data=response_data
        )


class SubmissionAPIKeyClient(BaseAPIKeyClient, SubmissionClient):
    """Client for managing Clappia submissions with API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize submission client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)


class SubmissionAuthTokenClient(BaseAuthTokenClient, SubmissionClient):
    """Client for managing Clappia submissions with auth token authentication."""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize submission client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
