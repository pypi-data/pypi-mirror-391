import builtins
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from aws_authenticator import cli as cli_mod


class DummySso:
    def __init__(self):
        self._accounts = [
            {"accountId": "111111111111", "accountName": "Dev (111111111111)"},
            {"accountId": "222222222222", "accountName": "Prod (222222222222)"},
        ]
        self._roles = {
            "111111111111": [{"roleName": "Admin"}, {"roleName": "ReadOnly"}],
            "222222222222": [{"roleName": "Admin"}],
        }

    def device_authorization(self):
        return {
            "clientId": "cid",
            "clientSecret": "csec",
            "clientSecretExpiresAt": 9999999999,
            "deviceCode": "dcode",
            "interval": 0,
            "expiresIn": 600,
            "verificationUri": "https://example/login"
        }

    def wait_for_token(self, **kwargs):
        return {"accessToken": "AT", "expiresIn": 600, "refreshToken": "RT"}

    def list_accounts(self, access_token):
        assert access_token == "AT"
        return self._accounts

    def list_account_roles(self, access_token, account_id):
        assert access_token == "AT"
        return self._roles[account_id]

    def get_role_credentials(self, access_token, account_id, role_name):
        assert access_token == "AT"
        return {
            "accessKeyId": "AKIA...",
            "secretAccessKey": "SECRET",
            "sessionToken": "TOKEN",
        }

    def refresh_access_token(self, client_id, client_secret, refresh_token):
        return {"accessToken": "AT2", "expiresIn": 600}


class DummyStore:
    def __init__(self, tmpdir):
        self.tmpdir = Path(tmpdir)
        self.cfg_path = self.tmpdir / "config.toml"
        self.state_path = self.tmpdir / "state.json"
        self.state = {}

    def load_config(self):
        return cli_mod.ToolConfig(
            sso_start_url="https://org.awsapps.com/start",
            sso_region="eu-west-1",
            default_cli_region="eu-west-1",
            profile_naming="{account_alias}-{account_id}-{role_name}",
        )

    def save_config(self, cfg):
        pass

    def load_state(self):
        return cli_mod.LastState(**self.state)

    def save_state(self, st):
        self.state = {
            k: getattr(st, k) for k in cli_mod.LastState.__annotations__.keys()
        }


class DummyAwsConfig:
    def __init__(self):
        self.profiles = {}

    def ensure_profile_with_credential_process(self, profile_name, proc_cmd, region):
        self.profiles[profile_name] = {"credential_process": proc_cmd, "region": region}


@pytest.fixture(autouse=True)
def patch_modules(monkeypatch, tmp_path):
    # Patch ConfigStore to avoid touching the real FS
    dummy_store = DummyStore(tmp_path)
    monkeypatch.setattr(cli_mod, "ConfigStore", lambda: dummy_store)
    # Patch SsoClient with our dummy implementation
    dummy_sso = DummySso()
    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: dummy_sso)
    # Patch AwsConfig to avoid writing ~/.aws/config
    monkeypatch.setattr(cli_mod, "AwsConfig", lambda: DummyAwsConfig())
    # Patch webbrowser.open to no-op
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", lambda *a, **k: True)
    return SimpleNamespace(store=dummy_store, sso=dummy_sso)


def test_login_interactive_selection(monkeypatch, capsys):
    # Simulate user selecting account 2 (Prod) and role 1 (Admin)
    inputs = iter(["2", "1"])  # account choice, then role choice
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))

    rc = cli_mod.cmd_login(SimpleNamespace())
    assert rc == 0
    out = capsys.readouterr().out
    assert "Configured AWS profile:" in out
    assert "export AWS_PROFILE=" in out


def test_credential_process_uses_cached_token(monkeypatch, capsys):
    # Prepare last state
    store = cli_mod.ConfigStore()  # patched
    st = store.load_state()
    st.last_account_id = "111111111111"
    st.last_role_name = "Admin"
    st.access_token = "AT"
    st.access_token_expires_at = 9999999999
    store.save_state(st)

    cfg = store.load_config()
    rc = cli_mod.credential_process_mode(cfg, store, None, None)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["Version"] == 1
    assert "AccessKeyId" in data


def test_refresh_updates_tokens(monkeypatch, capsys):
    # simulate last selection stored
    store = cli_mod.ConfigStore()
    st = store.load_state()
    st.last_account_id = "111111111111"
    st.last_role_name = "Admin"
    store.save_state(st)

    rc = cli_mod.cmd_refresh(SimpleNamespace())
    assert rc == 0
    out = capsys.readouterr().out
    assert "Authentication refreshed." in out
