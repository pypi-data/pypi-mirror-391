from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from zoho_projects_sdk.api.bugs import BugsAPI, ListParams
from zoho_projects_sdk.models.bug_models import (
    Issue,
    IssueCreateRequest,
    IssueUpdateRequest,
)


def test_portal_id_missing_raises_value_error() -> None:
    client = SimpleNamespace(portal_id=None)
    bugs_api = BugsAPI(client)

    with pytest.raises(ValueError, match="Portal ID is not configured"):
        _ = bugs_api._portal_id


def test_serialize_payload_with_pydantic_model_returns_dump() -> None:
    payload = BugsAPI._serialize_payload(IssueCreateRequest(name="Bug"))

    assert payload == {"name": "Bug"}


def test_serialize_payload_with_dict_filters_none() -> None:
    payload = BugsAPI._serialize_payload({"name": "Bug", "optional": None})

    assert payload == {"name": "Bug"}


def test_serialize_payload_rejects_unsupported_types() -> None:
    with pytest.raises(TypeError):
        BugsAPI._serialize_payload(42)


@pytest.mark.asyncio
async def test_list_by_portal_builds_params() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        get=AsyncMock(return_value={"bugs": [{"id": 1, "name": "Bug"}]}),
    )

    params = ListParams(
        page=2,
        per_page=5,
        sort_by="created_time",
        view_id="open",
        issue_ids="1,2",
        filter_={"status": "open"},
    )

    bugs = await BugsAPI(client).list_by_portal(params=params)

    assert len(bugs) == 1
    assert isinstance(bugs[0], Issue)
    client.get.assert_awaited_once()
    _, kwargs = client.get.call_args
    assert kwargs["params"] == {
        "page": 2,
        "per_page": 5,
        "sort_by": "created_time",
        "view_id": "open",
        "issue_ids": "1,2",
        "filter": '{"status": "open"}',
    }


@pytest.mark.asyncio
async def test_list_by_project_uses_project_endpoint() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        get=AsyncMock(return_value={"bugs": [{"id": 2, "name": "Bug"}]}),
    )

    params = ListParams(
        page=1,
        per_page=10,
        filter_="status:open",
    )

    bugs = await BugsAPI(client).list_by_project(
        project_id="proj",
        params=params,
    )

    assert len(bugs) == 1
    assert isinstance(bugs[0], Issue)
    client.get.assert_awaited_once_with(
        "/portal/portal-123/projects/proj/issues",
        params={"page": 1, "per_page": 10, "filter": "status:open"},
    )


@pytest.mark.asyncio
async def test_get_returns_constructed_issue_when_empty() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        get=AsyncMock(return_value={"bugs": []}),
    )

    issue = await BugsAPI(client).get(project_id="proj", issue_id="issue")

    assert isinstance(issue, Issue)
    assert issue.id is None


@pytest.mark.asyncio
async def test_get_returns_first_issue_when_present() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        get=AsyncMock(return_value={"bugs": [{"id": 7, "name": "Bug"}]}),
    )

    issue = await BugsAPI(client).get(project_id="proj", issue_id="issue")

    assert isinstance(issue, Issue)
    assert issue.id == 7


@pytest.mark.asyncio
async def test_create_prefers_issue_key() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        post=AsyncMock(return_value={"issue": {"id": 9, "name": "Bug"}}),
    )

    bug = await BugsAPI(client).create(
        project_id="proj", issue_data=IssueCreateRequest(name="Bug")
    )

    assert isinstance(bug, Issue)
    assert bug.id == 9
    client.post.assert_awaited_once_with(
        "/portal/portal-123/projects/proj/issues",
        json={"name": "Bug"},
    )


@pytest.mark.asyncio
async def test_create_falls_back_to_bug_key() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        post=AsyncMock(return_value={"bug": {"id": 10, "name": "Bug"}}),
    )

    bug = await BugsAPI(client).create(project_id="proj", issue_data={"name": "Bug"})

    assert isinstance(bug, Issue)
    assert bug.id == 10


@pytest.mark.asyncio
async def test_update_returns_issue() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        patch=AsyncMock(return_value={"issue": {"id": 11, "name": "Updated"}}),
    )
    payload = IssueUpdateRequest(name="Updated")

    bug = await BugsAPI(client).update(
        project_id="proj",
        issue_id="issue",
        issue_data=payload,
    )

    assert isinstance(bug, Issue)
    assert bug.id == 11
    client.patch.assert_awaited_once_with(
        "/portal/portal-123/projects/proj/issues/issue",
        json={"name": "Updated"},
    )


@pytest.mark.asyncio
async def test_delete_returns_true() -> None:
    client = SimpleNamespace(portal_id="portal-123", delete=AsyncMock())

    result = await BugsAPI(client).delete(project_id="proj", issue_id="issue")

    assert result is True
    client.delete.assert_awaited_once_with(
        "/portal/portal-123/projects/proj/issues/issue"
    )


@pytest.mark.asyncio
async def test_get_all_delegates_to_list_by_project() -> None:
    client = SimpleNamespace(
        portal_id="portal-123",
        get=AsyncMock(return_value={"bugs": []}),
    )

    bugs = await BugsAPI(client).get_all(project_id="proj", page=3, per_page=7)

    assert bugs == []
    client.get.assert_awaited_once_with(
        "/portal/portal-123/projects/proj/issues",
        params={"page": 3, "per_page": 7},
    )


def test_build_list_params_handles_filter_variants() -> None:
    list_params = ListParams(
        page=1,
        per_page=20,
        sort_by=None,
        view_id=None,
        issue_ids=None,
        filter_="status:open",
    )

    params = BugsAPI._build_list_params(list_params)

    assert params == {"page": 1, "per_page": 20, "filter": "status:open"}

    list_params = ListParams(
        page=4,
        per_page=50,
        sort_by="priority",
        view_id="backlog",
        issue_ids="1,2,3",
        filter_={"severity": "high"},
    )

    params = BugsAPI._build_list_params(list_params)

    assert params == {
        "page": 4,
        "per_page": 50,
        "sort_by": "priority",
        "view_id": "backlog",
        "issue_ids": "1,2,3",
        "filter": '{"severity": "high"}',
    }


def test_build_list_params_with_minimal_params() -> None:
    """Test _build_list_params with minimal/default parameters."""
    list_params = ListParams()  # Use defaults

    params = BugsAPI._build_list_params(list_params)

    assert params == {
        "page": 1,
        "per_page": 20,
    }


def test_build_list_params_ignores_none_values() -> None:
    """Test that _build_list_params ignores None values for optional fields."""
    list_params = ListParams(
        page=1,
        per_page=10,
        sort_by=None,  # Should be ignored
        view_id=None,  # Should be ignored
        issue_ids=None,  # Should be ignored
        filter_=None,  # Should be ignored
    )

    params = BugsAPI._build_list_params(list_params)

    assert params == {
        "page": 1,
        "per_page": 10,
    }


def test_build_list_params_with_string_filter() -> None:
    """Test _build_list_params with string filter (should pass through)."""
    list_params = ListParams(filter_="status:open AND priority:high")

    params = BugsAPI._build_list_params(list_params)

    assert params == {
        "page": 1,
        "per_page": 20,
        "filter": "status:open AND priority:high",
    }


def test_build_list_params_with_dict_filter() -> None:
    """Test _build_list_params with dict filter (should be JSON encoded)."""
    list_params = ListParams(
        filter_={"status": "open", "priority": ["high", "critical"]}
    )

    params = BugsAPI._build_list_params(list_params)

    assert params == {
        "page": 1,
        "per_page": 20,
        "filter": '{"status": "open", "priority": ["high", "critical"]}',
    }


def test_serialize_payload_with_issue_create_request() -> None:
    """Test _serialize_payload with IssueCreateRequest."""
    payload = BugsAPI._serialize_payload(
        IssueCreateRequest(
            name="Test Bug",
            description="Test description",
            severity={"id": 1, "name": "High"},
        )
    )

    assert payload == {
        "name": "Test Bug",
        "description": "Test description",
        "severity": {"id": 1, "name": "High"},
    }


def test_serialize_payload_with_issue_update_request() -> None:
    """Test _serialize_payload with IssueUpdateRequest."""
    payload = BugsAPI._serialize_payload(
        IssueUpdateRequest(name="Updated Bug", status={"id": 2, "name": "In Progress"})
    )

    assert payload == {
        "name": "Updated Bug",
        "status": {"id": 2, "name": "In Progress"},
    }


def test_serialize_payload_with_issue_model() -> None:
    """Test _serialize_payload with Issue model."""
    issue = Issue(id=123, name="Test Issue", description="Test description")

    payload = BugsAPI._serialize_payload(issue)

    assert payload == {
        "id": 123,
        "name": "Test Issue",
        "description": "Test description",
    }


def test_serialize_payload_with_dict_containing_none() -> None:
    """Test _serialize_payload with dict containing None values (should be filtered out)."""
    payload = BugsAPI._serialize_payload(
        {
            "name": "Test Bug",
            "description": None,  # Should be filtered out
            "severity": {"id": 1, "name": "High"},
            "optional_field": None,  # Should be filtered out
        }
    )

    assert payload == {"name": "Test Bug", "severity": {"id": 1, "name": "High"}}


def test_serialize_payload_with_empty_dict() -> None:
    """Test _serialize_payload with empty dict."""
    payload = BugsAPI._serialize_payload({})

    assert payload == {}


def test_serialize_payload_type_error_message() -> None:
    """Test _serialize_payload TypeError message for unsupported types."""
    with pytest.raises(TypeError) as exc_info:
        BugsAPI._serialize_payload(42)

    assert (
        "issue_data must be an IssueCreateRequest, IssueUpdateRequest, Issue, or dict"
        in str(exc_info.value)
    )


def test_list_params_default_values() -> None:
    """Test ListParams default values."""
    params = ListParams()

    assert params.page == 1
    assert params.per_page == 20
    assert params.sort_by is None
    assert params.view_id is None
    assert params.issue_ids is None
    assert params.filter_ is None


def test_list_params_with_all_values() -> None:
    """Test ListParams with all values set."""
    params = ListParams(
        page=5,
        per_page=50,
        sort_by="priority",
        view_id="open",
        issue_ids="1,2,3",
        filter_={"status": "open"},
    )

    assert params.page == 5
    assert params.per_page == 50
    assert params.sort_by == "priority"
    assert params.view_id == "open"
    assert params.issue_ids == "1,2,3"
    assert params.filter_ == {"status": "open"}


def test_issues_api_alias_exists() -> None:
    """Test that IssuesAPI alias exists and is the same as BugsAPI."""
    from zoho_projects_sdk.api.bugs import BugsAPI, IssuesAPI

    assert IssuesAPI is BugsAPI
