import pytest
from uuid import uuid4

from orchepy_client import OrchepyClient, OrchepyClientError, OrchepyNotFoundError


class TestOrchepyClient:
    """Test suite for OrchepyClient."""

    @pytest.fixture
    def client(self) -> OrchepyClient:
        """Create a test client instance."""
        return OrchepyClient(base_url="http://localhost:3296")

    def test_client_initialization(self) -> None:
        """Test client initialization."""
        client = OrchepyClient(base_url="http://localhost:3296")
        assert client.base_url == "http://localhost:3296"
        assert client.timeout == 10.0
        assert client.verify_ssl is True

    def test_client_initialization_with_custom_timeout(self) -> None:
        """Test client initialization with custom timeout."""
        client = OrchepyClient(base_url="http://localhost:3296", timeout=30.0)
        assert client.timeout == 30.0

    def test_client_initialization_strips_trailing_slash(self) -> None:
        """Test that trailing slash is removed from base_url."""
        client = OrchepyClient(base_url="http://localhost:3296/")
        assert client.base_url == "http://localhost:3296"

    @pytest.mark.asyncio
    async def test_create_workflow(
        self, client: OrchepyClient, httpx_mock: any
    ) -> None:
        """Test creating a workflow."""
        workflow_id = str(uuid4())
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:3296/workflows",
            json={
                "id": workflow_id,
                "name": "Test Workflow",
                "phases": ["Phase 1", "Phase 2"],
                "initial_phase": "Phase 1",
                "active": True,
            },
        )

        result = await client.create_workflow(
            name="Test Workflow",
            phases=["Phase 1", "Phase 2"],
            initial_phase="Phase 1",
        )

        assert result["id"] == workflow_id
        assert result["name"] == "Test Workflow"

    @pytest.mark.asyncio
    async def test_get_workflow(self, client: OrchepyClient, httpx_mock: any) -> None:
        """Test getting a workflow."""
        workflow_id = str(uuid4())
        httpx_mock.add_response(
            method="GET",
            url=f"http://localhost:3296/workflows/{workflow_id}",
            json={
                "id": workflow_id,
                "name": "Test Workflow",
                "phases": ["Phase 1"],
                "initial_phase": "Phase 1",
            },
        )

        result = await client.get_workflow(workflow_id)
        assert result["id"] == workflow_id

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(
        self, client: OrchepyClient, httpx_mock: any
    ) -> None:
        """Test getting a non-existent workflow."""
        workflow_id = str(uuid4())
        httpx_mock.add_response(
            method="GET",
            url=f"http://localhost:3296/workflows/{workflow_id}",
            status_code=404,
            text="Not found",
        )

        with pytest.raises(OrchepyNotFoundError) as exc_info:
            await client.get_workflow(workflow_id)

        assert exc_info.value.resource_type == "Workflow"
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_case(self, client: OrchepyClient, httpx_mock: any) -> None:
        """Test creating a case."""
        workflow_id = str(uuid4())
        case_id = str(uuid4())

        httpx_mock.add_response(
            method="POST",
            url="http://localhost:3296/cases",
            json={
                "id": case_id,
                "workflow_id": workflow_id,
                "current_phase": "Phase 1",
                "data": {"customer": "Acme Corp"},
            },
        )

        result = await client.create_case(
            workflow_id=workflow_id, data={"customer": "Acme Corp"}
        )

        assert result["id"] == case_id
        assert result["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_move_case(self, client: OrchepyClient, httpx_mock: any) -> None:
        """Test moving a case."""
        case_id = str(uuid4())

        httpx_mock.add_response(
            method="PUT",
            url=f"http://localhost:3296/cases/{case_id}/move",
            json={
                "id": case_id,
                "current_phase": "Phase 2",
            },
        )

        result = await client.move_case(
            case_id=case_id, to_phase="Phase 2", reason="Test move"
        )

        assert result["current_phase"] == "Phase 2"

    @pytest.mark.asyncio
    async def test_update_case_data(
        self, client: OrchepyClient, httpx_mock: any
    ) -> None:
        """Test updating case data."""
        case_id = str(uuid4())

        httpx_mock.add_response(
            method="PATCH",
            url=f"http://localhost:3296/cases/{case_id}/data",
            json={
                "id": case_id,
                "data": {"value": 75000},
            },
        )

        result = await client.update_case_data(case_id=case_id, data={"value": 75000})

        assert result["data"]["value"] == 75000

    @pytest.mark.asyncio
    async def test_send_notification(
        self, client: OrchepyClient, httpx_mock: any
    ) -> None:
        """Test sending a notification."""
        case_id = str(uuid4())

        httpx_mock.add_response(
            method="GET",
            url=f"http://localhost:3296/cases/{case_id}",
            json={
                "id": case_id,
                "data": {"notifications": []},
            },
        )

        httpx_mock.add_response(
            method="PATCH",
            url=f"http://localhost:3296/cases/{case_id}/data",
            json={
                "id": case_id,
                "data": {
                    "notifications": [
                        {"subject": "Test", "body": "Test body", "timestamp": None}
                    ]
                },
            },
        )

        await client.send_notification(
            case_id=case_id, subject="Test", body="Test body"
        )
