import logging
from typing import Any
from uuid import UUID

import httpx

from orchepy_client.exceptions import (
    OrchepyClientError,
    OrchepyHTTPError,
    OrchepyNotFoundError,
)
from orchepy_client.models import (
    CaseCreate,
    CaseDataUpdate,
    CaseMove,
    WorkflowCreate,
)

logger = logging.getLogger(__name__)


class OrchepyClient:
    """
    Async client for Orchepy API.

    This client provides a clean, type-safe interface to interact with the Orchepy
    workflow orchestration system.

    Example:
        >>> client = OrchepyClient(base_url="http://localhost:3296")
        >>> workflow = await client.create_workflow(
        ...     name="Sales Pipeline",
        ...     phases=["Lead", "Qualified", "Closed"],
        ...     initial_phase="Lead"
        ... )
        >>> case = await client.create_case(
        ...     workflow_id=workflow["id"],
        ...     data={"customer": "Acme Corp"}
        ... )
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        verify_ssl: bool = True,
    ) -> None:
        """
        Initialize Orchepy client.

        Args:
            base_url: Base URL of the Orchepy server (e.g., "http://localhost:3296")
            timeout: Request timeout in seconds (default: 10.0)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        logger.info(f"Orchepy client initialized for {self.base_url}")

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Make an HTTP request to the Orchepy API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., "/cases")
            json: JSON body for the request
            params: Query parameters

        Returns:
            JSON response as a dictionary or list

        Raises:
            OrchepyHTTPError: For HTTP errors
            OrchepyClientError: For other errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, verify=self.verify_ssl
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                )

                if response.status_code >= 400:
                    error_msg = (
                        f"{method} {endpoint} failed: "
                        f"{response.status_code} - {response.text}"
                    )
                    logger.error(error_msg)

                    if response.status_code == 404:
                        raise OrchepyHTTPError(error_msg, status_code=404)

                    raise OrchepyHTTPError(error_msg, status_code=response.status_code)

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HTTP error for {method} {endpoint}: {e}")
            raise OrchepyHTTPError(f"HTTP error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {endpoint}: {e}")
            raise OrchepyClientError(f"Unexpected error: {str(e)}")

    async def create_workflow(
        self,
        name: str,
        phases: list[str],
        initial_phase: str,
        active: bool = True,
        webhook_url: str | None = None,
        sla_config: dict[str, dict[str, int]] | None = None,
        automations: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            phases: List of phase names
            initial_phase: Name of the initial phase
            active: Whether the workflow is active (default: True)
            webhook_url: Optional webhook URL for notifications
            sla_config: Optional SLA configuration per phase
            automations: Optional automation configuration

        Returns:
            Created workflow data

        Example:
            >>> workflow = await client.create_workflow(
            ...     name="Sales Pipeline",
            ...     phases=["Lead", "Qualified", "Closed"],
            ...     initial_phase="Lead",
            ...     sla_config={"Lead": {"hours": 24}}
            ... )
        """
        workflow_data = WorkflowCreate(
            name=name,
            phases=phases,
            initial_phase=initial_phase,
            active=active,
            webhook_url=webhook_url,
            sla_config=sla_config,
            automations=automations,
        )

        logger.info(f"Creating workflow: {name}")
        result = await self._request(
            "POST", "/workflows", json=workflow_data.model_dump()
        )
        logger.info(f"Workflow created with ID {result['id']}")
        return result

    async def get_workflow(self, workflow_id: str | UUID) -> dict[str, Any]:
        """
        Get workflow information.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Workflow data

        Raises:
            OrchepyNotFoundError: If workflow not found
        """
        logger.info(f"Getting workflow {workflow_id}")

        try:
            return await self._request("GET", f"/workflows/{workflow_id}")
        except OrchepyHTTPError as e:
            if e.status_code == 404:
                raise OrchepyNotFoundError("Workflow", str(workflow_id))
            raise

    async def list_workflows(
        self,
        active: bool | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        List workflows.

        Args:
            active: Filter by active status
            limit: Maximum number of workflows to return

        Returns:
            List of workflow data
        """
        params: dict[str, Any] = {}
        if active is not None:
            params["active"] = active
        if limit is not None:
            params["limit"] = limit

        logger.info("Listing workflows")
        result = await self._request("GET", "/workflows", params=params)
        return result if isinstance(result, list) else [result]

    async def create_case(
        self,
        workflow_id: str | UUID,
        data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        initial_phase: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new case.

        Args:
            workflow_id: Workflow UUID
            data: Case data (custom fields)
            metadata: Optional metadata
            initial_phase: Optional initial phase (defaults to workflow's initial phase)

        Returns:
            Created case data including ID

        Example:
            >>> case = await client.create_case(
            ...     workflow_id="workflow-uuid",
            ...     data={"customer": "Acme Corp", "value": 50000},
            ...     metadata={"source": "api"}
            ... )
        """
        if isinstance(workflow_id, str):
            workflow_id = UUID(workflow_id)

        case_data = CaseCreate(
            workflow_id=workflow_id,
            data=data,
            metadata=metadata,
            initial_phase=initial_phase,
        )

        logger.info(f"Creating case in workflow {workflow_id}")
        result = await self._request("POST", "/cases", json=case_data.model_dump())
        logger.info(f"Case created with ID {result['id']}")
        return result

    async def get_case(self, case_id: str | UUID) -> dict[str, Any]:
        """
        Get case information.

        Args:
            case_id: Case UUID

        Returns:
            Case data

        Raises:
            OrchepyNotFoundError: If case not found
        """
        logger.info(f"Getting case {case_id}")

        try:
            return await self._request("GET", f"/cases/{case_id}")
        except OrchepyHTTPError as e:
            if e.status_code == 404:
                raise OrchepyNotFoundError("Case", str(case_id))
            raise

    async def list_cases(
        self,
        workflow_id: str | UUID | None = None,
        current_phase: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        List cases with optional filters.

        Args:
            workflow_id: Filter by workflow UUID
            current_phase: Filter by current phase name
            status: Filter by status (e.g., "active", "completed")
            limit: Maximum number of cases to return

        Returns:
            List of case data
        """
        params: dict[str, Any] = {}
        if workflow_id is not None:
            params["workflow_id"] = str(workflow_id)
        if current_phase is not None:
            params["current_phase"] = current_phase
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit

        logger.info("Listing cases")
        result = await self._request("GET", "/cases", params=params)
        return result if isinstance(result, list) else [result]

    async def move_case(
        self,
        case_id: str | UUID,
        to_phase: str,
        reason: str | None = None,
        triggered_by: str | None = None,
    ) -> dict[str, Any]:
        """
        Move a case to a different phase.

        Args:
            case_id: Case UUID
            to_phase: Target phase name
            reason: Optional reason for the move
            triggered_by: Optional identifier of who/what triggered the move

        Returns:
            Updated case data

        Example:
            >>> await client.move_case(
            ...     case_id="case-uuid",
            ...     to_phase="Qualified",
            ...     reason="Customer showed interest"
            ... )
        """
        move_data = CaseMove(
            to_phase=to_phase,
            reason=reason,
            triggered_by=triggered_by,
        )

        logger.info(f"Moving case {case_id} to phase '{to_phase}'")
        result = await self._request(
            "PUT", f"/cases/{case_id}/move", json=move_data.model_dump()
        )
        logger.info(f"Case {case_id} moved to '{to_phase}' successfully")
        return result

    async def update_case_data(
        self,
        case_id: str | UUID,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update case data fields.

        Args:
            case_id: Case UUID
            data: Fields to update (will be merged with existing data)

        Returns:
            Updated case data

        Example:
            >>> await client.update_case_data(
            ...     case_id="case-uuid",
            ...     data={"value": 75000, "notes": "Upgraded package"}
            ... )
        """
        update_data = CaseDataUpdate(data=data)

        logger.info(f"Updating case {case_id} data")
        result = await self._request(
            "PATCH", f"/cases/{case_id}/data", json=update_data.model_dump()
        )
        logger.info(f"Case {case_id} data updated successfully")
        return result

    async def get_case_history(self, case_id: str | UUID) -> list[dict[str, Any]]:
        """
        Get case phase transition history.

        Args:
            case_id: Case UUID

        Returns:
            List of history entries

        Example:
            >>> history = await client.get_case_history("case-uuid")
            >>> for entry in history:
            ...     print(f"{entry['from_phase']} -> {entry['to_phase']}")
        """
        logger.info(f"Getting history for case {case_id}")
        result = await self._request("GET", f"/cases/{case_id}/history")
        return result if isinstance(result, list) else [result]

    async def send_notification(
        self,
        case_id: str | UUID,
        subject: str,
        body: str,
    ) -> None:
        """
        Send a notification by storing it in case data.

        Note: Orchepy doesn't have built-in notifications like Pipefy.
        This method stores notifications in the case data under 'notifications' array.

        Args:
            case_id: Case UUID
            subject: Notification subject
            body: Notification body
        """
        logger.info(f"Sending notification to case {case_id}: {subject}")

        case_data = await self.get_case(case_id)
        current_data = case_data.get("data", {})

        notifications = current_data.get("notifications", [])
        notifications.append(
            {
                "subject": subject,
                "body": body,
                "timestamp": None,
            }
        )

        await self.update_case_data(
            case_id=case_id,
            data={"notifications": notifications},
        )

        logger.info(f"Notification sent to case {case_id}")
