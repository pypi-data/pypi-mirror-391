"""Backward compatibility exports for the deprecated bug models module."""

from __future__ import annotations

from .issue_models import (
    Issue,
    IssueAssignee,
    IssueCreateRequest,
    IssueReference,
    IssueReminder,
    IssueTagMutation,
    IssueTagsUpdate,
    IssueUpdateRequest,
)

# Re-export legacy names for downstream compatibility
Bug = Issue
BugCreateRequest = IssueCreateRequest
BugUpdateRequest = IssueUpdateRequest

__all__ = [
    "Issue",
    "IssueReference",
    "IssueAssignee",
    "IssueReminder",
    "IssueTagMutation",
    "IssueTagsUpdate",
    "IssueCreateRequest",
    "IssueUpdateRequest",
    "Bug",
    "BugCreateRequest",
    "BugUpdateRequest",
]
