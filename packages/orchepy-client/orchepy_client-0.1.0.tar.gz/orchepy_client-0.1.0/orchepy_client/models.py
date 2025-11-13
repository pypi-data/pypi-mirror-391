from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowCreate(BaseModel):
    """Request model for creating a workflow."""

    name: str
    phases: list[str]
    initial_phase: str
    active: bool = True
    webhook_url: str | None = None
    sla_config: dict[str, dict[str, int]] | None = None
    automations: dict[str, Any] | None = None


class WorkflowResponse(BaseModel):
    """Response model for workflow data."""

    id: UUID
    name: str
    phases: list[str]
    initial_phase: str
    active: bool
    webhook_url: str | None = None
    sla_config: dict[str, dict[str, int]] | None = None
    automations: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class CaseCreate(BaseModel):
    """Request model for creating a case."""

    workflow_id: UUID
    data: dict[str, Any]
    metadata: dict[str, Any] | None = None
    initial_phase: str | None = None


class CaseMove(BaseModel):
    """Request model for moving a case."""

    to_phase: str
    reason: str | None = None
    triggered_by: str | None = None


class CaseDataUpdate(BaseModel):
    """Request model for updating case data."""

    data: dict[str, Any]


class CaseResponse(BaseModel):
    """Response model for case data."""

    id: UUID
    workflow_id: UUID
    current_phase: str
    status: str
    data: dict[str, Any]
    metadata: dict[str, Any] | None = None
    phase_entered_at: datetime
    created_at: datetime
    updated_at: datetime


class CaseHistoryEntry(BaseModel):
    """Response model for a single case history entry."""

    id: UUID
    case_id: UUID
    from_phase: str | None
    to_phase: str
    reason: str | None = None
    triggered_by: str | None = None
    occurred_at: datetime


class CaseHistoryResponse(BaseModel):
    """Response model for case history."""

    case_id: UUID
    history: list[CaseHistoryEntry]
