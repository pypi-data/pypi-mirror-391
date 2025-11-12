"""Unit tests for Issue Pydantic model behaviour."""

from zoho_projects_sdk.models import Issue


def test_issue_accepts_title_alias_and_optional_fields() -> None:
    payload = {
        "id": 101,
        "title": "Critical issue",
        "status": {"name": "Open"},
        "severity": "High",
        "attachments": [1, 2],
        "tags": ["backend"],
    }

    bug = Issue.model_validate(payload)

    assert bug.id == 101
    assert bug.name == "Critical issue"
    assert bug.status == {"name": "Open"}
    assert bug.attachments == [1, 2]
    assert bug.tags == ["backend"]


def test_issue_title_property_returns_name() -> None:
    bug = Issue(id=2, name="UI Bug")

    assert bug.title == "UI Bug"
