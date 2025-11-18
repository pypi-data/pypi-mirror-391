from __future__ import annotations

import builtins
import json
from types import SimpleNamespace

import pytest

from aws_authenticator import cli as cli_mod


def test_select_from_list_uses_default(monkeypatch, capsys):
    # Provide empty input to trigger default selection
    items = [("a", "Alpha"), ("b", "Beta")]
    monkeypatch.setattr(builtins, "input", lambda *a, **k: "")
    key, label = cli_mod._select_from_list("Title", items, default_idx=0)
    assert key == "a" and label == "Alpha"


def test_prompt_returns_default(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *a, **k: "")
    val = cli_mod._prompt("Enter", default="X")
    assert val == "X"


def test_cmd_refresh_without_selection_returns_code_2(capsys, monkeypatch):
    # Patch store with empty state
    class DummyStore:
        def load_config(self):
            return cli_mod.ToolConfig(sso_start_url="http://start", sso_region="eu-west-1")

        def load_state(self):
            return cli_mod.LastState()

    monkeypatch.setattr(cli_mod, "ConfigStore", lambda: DummyStore())
    rc = cli_mod.cmd_refresh(SimpleNamespace())
    assert rc == 2
    out = capsys.readouterr().out
    assert "No previous account/role selection" in out


def test_run_selection_no_accounts_exits(monkeypatch):
    class DummySso:
        def list_accounts(self, access_token):
            return []

    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: DummySso())
    store = type("S", (), {"load_state": lambda self: cli_mod.LastState()})()
    cfg = cli_mod.ToolConfig(sso_start_url="http://start", sso_region="eu-west-1", profile_naming="{account_alias}-{account_id}-{role_name}")
    with pytest.raises(SystemExit) as se:
        cli_mod.run_selection(cfg, store, access_token="AT")
    assert se.value.code == 3


def test_run_selection_no_roles_exits(monkeypatch):
    class DummySso:
        def list_accounts(self, access_token):
            return [{"accountId": "1", "accountName": "A (1)"}]

        def list_account_roles(self, access_token, account_id):
            return []

    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: DummySso())
    # Simulate pressing Enter for defaults
    monkeypatch.setattr(builtins, "input", lambda *a, **k: "1")
    store = type("S", (), {"load_state": lambda self: cli_mod.LastState()})()
    cfg = cli_mod.ToolConfig(sso_start_url="http://start", sso_region="eu-west-1", profile_naming="{account_alias}-{account_id}-{role_name}")
    with pytest.raises(SystemExit) as se:
        cli_mod.run_selection(cfg, store, access_token="AT")
    assert se.value.code == 4


def test_credential_process_authorization_required_when_expired_no_refresh(monkeypatch, capsys):
    # Prepare store with expired access token and no refresh
    class DummyStore:
        def __init__(self):
            self.state = cli_mod.LastState(last_account_id="1", last_role_name="Admin", access_token="AT", access_token_expires_at=0)

        def load_config(self):
            return cli_mod.ToolConfig(sso_start_url="http://start", sso_region="eu-west-1")

        def load_state(self):
            return self.state

        def save_state(self, st):
            self.state = st

    class DummySso:
        def get_role_credentials(self, access_token, account_id, role_name):
            raise AssertionError("should not be called without valid token")

    store = DummyStore()
    monkeypatch.setattr(cli_mod, "ConfigStore", lambda: store)
    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: DummySso())

    rc = cli_mod.credential_process_mode(store.load_config(), store, None, None)
    assert rc == 1
    data = json.loads(capsys.readouterr().out)
    assert data["Error"] == "AuthorizationRequired"


def test_credential_process_uses_overrides(monkeypatch, capsys):
    # Ensure overrides for account and role are used
    import time
    class CheckSso:
        def __init__(self):
            self.called = None

        def get_role_credentials(self, access_token, account_id, role_name):
            self.called = (access_token, account_id, role_name)
            return {"accessKeyId": "AK", "secretAccessKey": "SK", "sessionToken": "ST"}

    inst = CheckSso()

    class DummyStore:
        def load_config(self):
            return cli_mod.ToolConfig(sso_start_url="http://start", sso_region="eu-west-1")

        def load_state(self):
            st = cli_mod.LastState(last_account_id="X", last_role_name="Y", access_token="AT", access_token_expires_at=int(time.time()) + 3600)
            return st

        def save_state(self, st):
            pass

    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: inst)
    store = DummyStore()
    rc = cli_mod.credential_process_mode(store.load_config(), store, account_override="OVACC", role_override="OVROLE")
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["AccessKeyId"] == "AK"
    assert inst.called[1:] == ("OVACC", "OVROLE")


def test_perform_sso_login_missing_config_exits(monkeypatch):
    cfg = cli_mod.ToolConfig()  # missing sso settings
    store = type("S", (), {"load_state": lambda self: cli_mod.LastState(), "save_state": lambda self, st: None})()
    with pytest.raises(SystemExit) as se:
        cli_mod.perform_sso_login(cfg, store, open_browser=False)
    assert se.value.code == 2
