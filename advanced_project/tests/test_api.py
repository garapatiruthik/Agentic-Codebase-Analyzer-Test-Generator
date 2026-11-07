import sys
from pathlib import Path
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
import pytest

# Make imports deterministic whether pytest is launched from the repository root or
# from advanced_project.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main import app
from src.pipeline import _validate_tool_call


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_returns_report_for_requested_directory(tmp_path, monkeypatch):
    pipeline = AsyncMock(return_value="# Audit report")
    monkeypatch.setattr("src.main.run_full_research_pipeline", pipeline)

    response = client.post(
        "/run",
        json={"query": "Review this project", "target_dir": str(tmp_path)},
    )

    assert response.status_code == 200
    assert response.json() == {"report": "# Audit report"}
    pipeline.assert_awaited_once_with(
        user_query="Review this project",
        target_directory=tmp_path.resolve(),
    )


def test_run_rejects_blank_query(tmp_path):
    response = client.post(
        "/run",
        json={"query": "  ", "target_dir": str(tmp_path)},
    )

    assert response.status_code == 422


def test_run_rejects_missing_target_directory(tmp_path):
    response = client.post(
        "/run",
        json={"query": "Review this project", "target_dir": str(tmp_path / "missing")},
    )

    assert response.status_code == 422


def test_run_rejects_relative_target_directory():
    response = client.post(
        "/run",
        json={"query": "Review this project", "target_dir": "."},
    )

    assert response.status_code == 422


def test_missing_api_key_is_reported_without_starting_mcp(tmp_path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = client.post(
        "/run",
        json={"query": "Review this project", "target_dir": str(tmp_path)},
    )

    assert response.status_code == 503
    assert "GROQ_API_KEY" in response.json()["detail"]


def test_filesystem_tools_cannot_write_or_read_outside_target(tmp_path):
    outside_file = tmp_path.parent / "outside.py"

    for tool_call in (
        {"name": "write_file", "args": {"path": str(tmp_path / "new.py")}},
        {"name": "read_file", "args": {"path": str(outside_file)}},
    ):
        with pytest.raises(PermissionError):
            _validate_tool_call(tool_call, tmp_path)


def test_filesystem_tools_cannot_read_credentials_or_data(tmp_path):
    for filename in (".env", "records.csv", "dataset.json"):
        with pytest.raises(PermissionError):
            _validate_tool_call(
                {"name": "read_file", "args": {"path": str(tmp_path / filename)}},
                tmp_path,
            )


def test_filesystem_tools_can_read_project_source_and_manifests(tmp_path):
    for filename in ("app.py", "package.json", ".env.example"):
        _validate_tool_call(
            {"name": "read_file", "args": {"path": str(tmp_path / filename)}},
            tmp_path,
        )
