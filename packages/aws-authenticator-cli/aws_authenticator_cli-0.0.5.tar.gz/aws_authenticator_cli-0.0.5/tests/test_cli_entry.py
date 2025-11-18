from __future__ import annotations

import builtins
import json
import sys
from types import SimpleNamespace

import pytest

from aws_authenticator import cli as cli_mod


class DummySso:
    def device_authorization(self):
        return {
            "clientId": "cid",
            "clientSecret": "csec",
            "clientSecretExpiresAt": 9999999999,
            "deviceCode": "dcode",
            "interval": 0,
            "expiresIn": 600,
        }

    def wait_for_token(self, **kwargs):
        return {"accessToken": "AT", "expiresIn": 600}

    def list_accounts(self, access_token):
        return [{"accountId": "1", "accountName": "A (1)"}]

    def list_account_roles(self, access_token, account_id):
        return [{"roleName": "Admin"}]

    def get_role_credentials(self, access_token, account_id, role_name):
        return {"accessKeyId": "AK", "secretAccessKey": "SK", "sessionToken": "ST"}


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    import time as _time
    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: DummySso())
    def _load_config(self):
        return cli_mod.ToolConfig(sso_start_url="http://start", sso_region="eu-west-1", default_cli_region="eu-west-1")
    def _load_state(self):
        # Provide a valid, non-expired access token so credential_process succeeds
        return cli_mod.LastState(last_account_id="1", last_role_name="Admin", access_token="AT", access_token_expires_at=int(_time.time()) + 3600)
    def _save_state(self, st):
        return None
    def _save_config(self, cfg):
        return None
    dummy_store = type("S", (), {
        "load_config": _load_config,
        "load_state": _load_state,
        "save_state": _save_state,
        "save_config": _save_config,
    })()
    monkeypatch.setattr(cli_mod, "ConfigStore", lambda: dummy_store)
    return SimpleNamespace(store=dummy_store)


def test_main_help_shows_when_no_command(capsys):
    # Simulate running without args
    sys.argv = ["aws-authenticator"]
    with pytest.raises(SystemExit) as se:
        cli_mod.main()
    assert se.value.code == 0
    out = capsys.readouterr().out
    assert "usage:" in out


def test_main_dispatch_credential_process(capsys):
    sys.argv = [
        "aws-authenticator",
        "--credential-process",
        "--account", "1",
        "--role", "Admin",
    ]
    with pytest.raises(SystemExit) as se:
        cli_mod.main()
    assert se.value.code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["Version"] == 1
    assert data["AccessKeyId"] == "AK"


def test_main_dispatch_commands_login(monkeypatch, capsys):
    inputs = iter(["1", "1"])  # select account and role
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))
    sys.argv = ["aws-authenticator", "login"]
    with pytest.raises(SystemExit) as se:
        cli_mod.main()
    assert se.value.code == 0
    out = capsys.readouterr().out
    assert "Configured AWS profile:" in out


def test_main_dispatch_commands_setup(monkeypatch):
    inputs = iter(["http://new", "eu-west-1", "eu-west-1", "{role_name}"])
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))
    sys.argv = ["aws-authenticator", "setup"]
    with pytest.raises(SystemExit) as se:
        cli_mod.main()
    assert se.value.code == 0


def test_main_dispatch_commands_refresh():
    sys.argv = ["aws-authenticator", "refresh"]
    with pytest.raises(SystemExit) as se:
        cli_mod.main()
    assert se.value.code == 0
