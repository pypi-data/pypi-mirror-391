#! /usr/bin/env python
# -*- coding: utf-8 -*-
# tests/test_cli.py

from contextlib import contextmanager
from pathlib import Path

import pytest
import requests
from typer.testing import CliRunner

from gladiator.cli import app


@pytest.fixture(autouse=True)
def _clear_login_env(monkeypatch):
    """Ensure arena login env vars never leak into tests."""
    monkeypatch.delenv("GLADIATOR_USERNAME", raising=False)
    monkeypatch.delenv("GLADIATOR_PASSWORD", raising=False)


@contextmanager
def _noop_spinner(*_args, **_kwargs):
    yield


def test_upload_weblink_truncates_edition(monkeypatch):
    runner = CliRunner()
    captured = {}

    class DummyClient:
        def upload_weblink_to_working(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())

    long_edition = "x" * 40
    result = runner.invoke(
        app,
        [
            "upload-weblink",
            "510-0001",
            "https://example.com/resource",
            "--edition",
            long_edition,
        ],
    )

    assert result.exit_code == 0
    assert captured["edition"] == long_edition[:16]


def test_upload_weblink_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def upload_weblink_to_working(self, **kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["upload-weblink", "510-0001", "https://example.com/resource"],
    )

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_upload_weblink_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def upload_weblink_to_working(self, **kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("web upload blocked")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["upload-weblink", "510-0001", "https://example.com/resource"],
    )

    assert result.exit_code == 2
    assert "web upload blocked" in result.stderr


def test_upload_file_truncates_edition(monkeypatch, tmp_path):
    runner = CliRunner()
    captured = {}

    class DummyClient:
        def upload_file_to_working(self, item, file_path, reference, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())

    dummy = tmp_path / "firmware.bin"
    dummy.write_text("hi")

    long_edition = "ABCDEF0123456789ZYXWV"  # 21 chars
    result = runner.invoke(
        app,
        [
            "upload-file",
            "510-0001",
            str(dummy),
            "--edition",
            long_edition,
        ],
    )

    assert result.exit_code == 0
    assert captured["edition"] == long_edition[:16]


def test_upload_file_http_error(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyClient:
        def upload_file_to_working(self, *args, **kwargs):
            raise requests.HTTPError("boom")

    dummy = tmp_path / "fw.bin"
    dummy.write_text("x")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["upload-file", "510-0001", str(dummy)])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_upload_file_arena_error(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyClient:
        def upload_file_to_working(self, *args, **kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("upload blocked")

    dummy = tmp_path / "fw.bin"
    dummy.write_text("x")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["upload-file", "510-0001", str(dummy)])

    assert result.exit_code == 2
    assert "upload blocked" in result.stderr


def test_login_success(monkeypatch):
    runner = CliRunner()
    saved = {}

    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "OK"

        def raise_for_status(self):
            return None

        def json(self):
            return {"arena_session_id": "ABC123"}

    class DummySession:
        def __init__(self):
            self.verify = None
            self.post_calls = []

        def post(self, url, headers=None, json=None):
            self.post_calls.append({"url": url, "headers": headers, "json": json})
            return DummyResponse()

    dummy_session = DummySession()

    monkeypatch.setattr("gladiator.cli.requests.Session", lambda: dummy_session)
    monkeypatch.setattr(
        "gladiator.cli.save_config_raw", lambda data: saved.update(data)
    )
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "login",
            "--username",
            "user@example.com",
            "--password",
            "s3cr3t",
            "--base-url",
            "https://arena.test/api",
            "--reason",
            "CI",
        ],
    )

    assert result.exit_code == 0
    assert dummy_session.verify is True
    assert saved["base_url"] == "https://arena.test/api"
    assert saved["reason"] == "CI"
    assert dummy_session.post_calls
    post_call = dummy_session.post_calls[0]
    assert post_call["url"] == "https://arena.test/api/login"
    assert post_call["json"] == {"email": "user@example.com", "password": "s3cr3t"}
    assert post_call["headers"]["Arena-Usage-Reason"] == "CI"
    assert "Saved session" in result.stdout


def test_login_ci_requires_credentials(monkeypatch):
    runner = CliRunner()

    class DummySession:
        def __init__(self):
            self.post_calls = []

        def post(self, *_args, **_kwargs):
            self.post_calls.append((_args, _kwargs))
            raise AssertionError("POST should not be called when credentials missing")

    dummy_session = DummySession()

    session_calls = []

    def _session_factory():
        session_calls.append(True)
        return dummy_session

    monkeypatch.setattr("gladiator.cli.requests.Session", _session_factory)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["login", "--ci", "--password", "secret"])

    assert result.exit_code == 2
    assert "Provide --username and --password" in result.stderr
    assert not session_calls


def test_login_http_failure(monkeypatch):
    runner = CliRunner()
    saved = {}

    class DummyResponse:
        def __init__(self):
            self.text = "boom"

        def raise_for_status(self):
            raise requests.HTTPError("bad request")

        def json(self):
            return {}

    class DummySession:
        def __init__(self):
            self.verify = None
            self.post_calls = []

        def post(self, url, headers=None, json=None):
            self.post_calls.append({"url": url, "headers": headers, "json": json})
            return DummyResponse()

    monkeypatch.setattr("gladiator.cli.requests.Session", lambda: DummySession())
    monkeypatch.setattr(
        "gladiator.cli.save_config_raw", lambda data: saved.update(data)
    )
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "login",
            "--username",
            "user@example.com",
            "--password",
            "s3cr3t",
        ],
    )

    assert result.exit_code == 2
    assert "Login failed" in result.stderr
    assert saved == {}


def test_latest_approved_success(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def get_latest_approved_revision(self, item):
            self.calls.append(item)
            return "B"

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0001"])

    assert result.exit_code == 0
    assert client.calls == ["510-0001"]
    assert result.stdout.strip() == "B"


def test_latest_approved_json_output(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            return "C"

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["latest-approved", "510-0002", "--format", "json"],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == '{\n  "article": "510-0002",\n  "revision": "C"\n}'


def test_latest_approved_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0003"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_latest_approved_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            from gladiator.arena import ArenaError

            raise ArenaError("no revision")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0004"])

    assert result.exit_code == 2
    assert "no revision" in result.stderr


def test_list_files_success(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def list_files(self, item, revision):
            self.calls.append((item, revision))
            return [
                {
                    "title": "Firmware",
                    "name": "fw.bin",
                    "size": 1024,
                    "edition": "A",
                    "storageMethodName": "FILE",
                    "location": None,
                }
            ]

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["list-files", "510-0005"])

    assert result.exit_code == 0
    assert client.calls == [("510-0005", None)]
    assert "fw.bin" in result.stdout
    assert "1024" in result.stdout


def test_list_files_json(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def list_files(self, item, revision):
            return [{"name": "fw.bin"}]

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["list-files", "510-0006", "--rev", "WORKING", "--format", "json"],
    )

    assert result.exit_code == 0
    assert (
        result.stdout.strip()
        == '{\n  "article": "510-0006",\n  "revision": "WORKING",\n  "files": [\n    {\n      "name": "fw.bin"\n    }\n  ]\n}'
    )


def test_list_files_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def list_files(self, item, revision):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["list-files", "510-0007"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_list_files_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def list_files(self, item, revision):
            from gladiator.arena import ArenaError

            raise ArenaError("no files")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["list-files", "510-0008"])

    assert result.exit_code == 2
    assert "no files" in result.stderr


def test_bom_table(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            assert recursive is False
            assert max_depth is None
            return [
                {
                    "lineNumber": 1,
                    "quantity": 2,
                    "itemNumber": "510-CH-A",
                    "itemName": "Child A",
                    "refDes": "R1",
                    "level": 0,
                }
            ]

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["bom", "510-0009"])

    assert result.exit_code == 0
    assert "510-CH-A" in result.stdout
    assert "Child A" in result.stdout


def test_bom_json(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            assert recursive is True
            assert max_depth == 2
            return []

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "bom",
            "510-0010",
            "--rev",
            "WORKING",
            "--output",
            "json",
            "--recursive",
            "--max-depth",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == '{\n  "count": 0,\n  "results": []\n}'


def test_bom_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["bom", "510-0011"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_bom_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            from gladiator.arena import ArenaError

            raise ArenaError("bad bom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["bom", "510-0012"])

    assert result.exit_code == 2
    assert "bad bom" in result.stderr


def test_get_files_default(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def download_files(self, item, revision, out_dir):
            self.calls.append((item, revision, out_dir))
            return [out_dir / "fw.bin"]

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-files", "510-0013"])

    assert result.exit_code == 0
    assert client.calls == [("510-0013", None, Path("510-0013"))]
    assert result.stdout.strip() == str(Path("510-0013") / "fw.bin")


def test_get_files_recursive(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.recursive_calls = []

        def download_files_recursive(self, item, revision, out_dir, max_depth):
            self.recursive_calls.append((item, revision, out_dir, max_depth))
            return [out_dir / "fw.bin"]

        def download_files(self, *args, **kwargs):
            raise AssertionError("Expected recursive path")

    client = DummyClient()
    target_dir = tmp_path / "artifacts"

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "get-files",
            "510-0014",
            "--rev",
            "WORKING",
            "--out",
            str(target_dir),
            "--recursive",
            "--max-depth",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert client.recursive_calls == [("510-0014", "WORKING", target_dir, 2)]
    assert result.stdout.strip() == str(target_dir / "fw.bin")


def test_get_files_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def download_files(self, item, revision, out_dir):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-files", "510-0015"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_get_files_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def download_files(self, item, revision, out_dir):
            from gladiator.arena import ArenaError

            raise ArenaError("download blocked")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-files", "510-0016"])

    assert result.exit_code == 2
    assert "download blocked" in result.stderr
