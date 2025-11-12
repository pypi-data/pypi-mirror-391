"""Tests for the bug_models module backward compatibility exports."""

from __future__ import annotations

from zoho_projects_sdk.models.bug_models import (
    Bug,
    BugCreateRequest,
    BugUpdateRequest,
    Issue,
    IssueCreateRequest,
    IssueUpdateRequest,
)


def test_bug_models_exports_all_symbols() -> None:
    """Test that all expected symbols are exported from bug_models."""
    from zoho_projects_sdk.models import bug_models

    expected_exports = [
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

    for export in expected_exports:
        assert hasattr(bug_models, export), f"Missing export: {export}"


def test_bug_is_issue_alias() -> None:
    """Test that Bug is an alias for Issue for backward compatibility."""
    assert Bug is Issue

    # Test that they can be used interchangeably
    issue_data = {"id": 1, "name": "Test Issue"}

    issue = Issue.model_validate(issue_data)
    bug = Bug.model_validate(issue_data)

    assert issue.id == bug.id
    assert issue.name == bug.name
    assert type(issue) is type(bug)


def test_bug_create_request_is_issue_create_request_alias() -> None:
    """Test that BugCreateRequest is an alias for IssueCreateRequest."""
    assert BugCreateRequest is IssueCreateRequest

    # Test functionality
    request_data = {"name": "Test Bug"}

    issue_request = IssueCreateRequest.model_validate(request_data)
    bug_request = BugCreateRequest.model_validate(request_data)

    assert issue_request.name == bug_request.name
    assert type(issue_request) is type(bug_request)


def test_bug_update_request_is_issue_update_request_alias() -> None:
    """Test that BugUpdateRequest is an alias for IssueUpdateRequest."""
    assert BugUpdateRequest is IssueUpdateRequest

    # Test functionality
    request_data = {"name": "Updated Bug"}

    issue_request = IssueUpdateRequest.model_validate(request_data)
    bug_request = BugUpdateRequest.model_validate(request_data)

    assert issue_request.name == bug_request.name
    assert type(issue_request) is type(bug_request)


def test_backward_compatibility_imports() -> None:
    """Test that backward compatibility imports work as expected."""
    # These should all work without raising ImportError
    # And the original Issue models should also be available
    from zoho_projects_sdk.models.bug_models import Bug  # noqa: F401
    from zoho_projects_sdk.models.bug_models import BugCreateRequest  # noqa: F401
    from zoho_projects_sdk.models.bug_models import BugUpdateRequest  # noqa: F401
    from zoho_projects_sdk.models.bug_models import Issue  # noqa: F401
    from zoho_projects_sdk.models.bug_models import IssueCreateRequest  # noqa: F401
    from zoho_projects_sdk.models.bug_models import IssueUpdateRequest  # noqa: F401


def test_bug_models_inheritance_preserves_functionality() -> None:
    """Test that the aliasing preserves all Issue functionality."""
    # Create an Issue
    issue = Issue(
        id=123, name="Test Issue", description="Test description", priority="High"
    )

    # Create a Bug with same data
    bug = Bug(
        id=123, name="Test Issue", description="Test description", priority="High"
    )

    # They should be identical
    assert issue.model_dump() == bug.model_dump()
    assert issue.model_fields_set == bug.model_fields_set


def test_bug_models_with_complex_data() -> None:
    """Test bug models with complex nested data structures."""
    complex_data = {
        "id": 456,
        "name": "Complex Bug",
        "assignee": {"id": "user123", "name": "Test User"},
        "tags": ["bug", "critical", "backend"],
        "status": {"id": 1, "name": "Open"},
    }

    # Test with Issue
    issue = Issue.model_validate(complex_data)

    # Test with Bug alias
    bug = Bug.model_validate(complex_data)

    assert issue.id == bug.id == 456
    assert issue.name == bug.name == "Complex Bug"
    assert issue.assignee == bug.assignee
    assert issue.tags == bug.tags


def test_bug_create_request_functionality() -> None:
    """Test BugCreateRequest functionality."""
    bug_request = BugCreateRequest(
        name="New Bug",
        description="Bug description",
        severity={"id": 1, "name": "Critical"},
    )

    assert bug_request.name == "New Bug"
    assert bug_request.description == "Bug description"
    assert bug_request.severity == {"id": 1, "name": "Critical"}

    # Test serialization
    serialized = bug_request.model_dump(exclude_none=True)
    assert "name" in serialized
    assert "description" in serialized
    assert "severity" in serialized


def test_bug_update_request_functionality() -> None:
    """Test BugUpdateRequest functionality."""
    update_request = BugUpdateRequest(
        name="Updated Bug", status={"id": 2, "name": "In Progress"}
    )

    assert update_request.name == "Updated Bug"
    assert update_request.status == {"id": 2, "name": "In Progress"}

    # Test serialization
    serialized = update_request.model_dump(exclude_none=True)
    assert "name" in serialized
    assert "status" in serialized


def test_all_issue_models_available() -> None:
    """Test that all Issue models are properly exported."""
    # Test that all Issue models are properly exported
    from zoho_projects_sdk.models.bug_models import (
        IssueAssignee,
        IssueReference,
        IssueReminder,
        IssueTagMutation,
        IssueTagsUpdate,
    )

    # Test that these are importable and are the correct types
    assert IssueReference is not None
    assert IssueAssignee is not None
    assert IssueReminder is not None
    assert IssueTagMutation is not None
    assert IssueTagsUpdate is not None
