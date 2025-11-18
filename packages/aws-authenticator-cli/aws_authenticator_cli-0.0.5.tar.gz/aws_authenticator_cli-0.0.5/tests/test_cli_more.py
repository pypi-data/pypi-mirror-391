from __future__ import annotations

import builtins
import json
from types import SimpleNamespace

import pytest

from aws_authenticator import cli as cli_mod


class DummySsoErr:
    def device_authorization(self):
        raise cli_mod.SsoLoginError("boom")


class DummyAwsConfig:
    def __init__(self):
        self.calls = []

    def ensure_profile_with_credential_process(self, profile_name, proc_cmd, region):
        self.calls.append((profile_name, proc_cmd, region))


class DummyStore:
    def __init__(self):
        self.state = {}
        self.saved_cfg = None

    def load_config(self):
        return cli_mod.ToolConfig(
            sso_start_url="https://org.awsapps.com/start",
            sso_region="eu-west-1",
            default_cli_region="eu-west-1",
            profile_naming="{account_alias}-{account_id}-{role_name}",
        )

    def save_config(self, cfg):
        self.saved_cfg = cfg

    def load_state(self):
        return cli_mod.LastState(**self.state)

    def save_state(self, st):
        self.state = {k: getattr(st, k) for k in cli_mod.LastState.__annotations__.keys()}


@pytest.fixture
def patch_base(monkeypatch):
    # default DummySso for most tests
    class DummySso:
        def device_authorization(self):
            return {
                "clientId": "cid",
                "clientSecret": "csec",
                "clientSecretExpiresAt": 9999999999,
                "deviceCode": "dcode",
                "interval": 0,
                "expiresIn": 600,
                "verificationUri": "https://example/login",
            }

        def wait_for_token(self, **kwargs):
            return {"accessToken": "AT", "expiresIn": 600, "refreshToken": "RT"}

        def list_accounts(self, access_token):
            return [{"accountId": "111111111111", "accountName": "Dev (111111111111)"}]

        def list_account_roles(self, access_token, account_id):
            return [{"roleName": "Admin"}]

        def get_role_credentials(self, access_token, account_id, role_name):
            return {
                "accessKeyId": "AKIA...",
                "secretAccessKey": "SECRET",
                "sessionToken": "TOKEN",
            }

        def refresh_access_token(self, client_id, client_secret, refresh_token):
            return {"accessToken": "AT2", "expiresIn": 600}

    dummy_store = DummyStore()
    monkeypatch.setattr(cli_mod, "ConfigStore", lambda: dummy_store)
    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: DummySso())
    monkeypatch.setattr(cli_mod, "AwsConfig", lambda: DummyAwsConfig())
    # webbrowser no-op
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", lambda *a, **k: True)
    return SimpleNamespace(store=dummy_store)


def test_setup_prompts_and_saves(patch_base, monkeypatch):
    # Provide new values for all prompts
    inputs = iter([
        "https://new.awsapps.com/start",
        "us-east-1",
        "us-east-1",
        "{account_id}-{role_name}",
    ])
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))
    rc = cli_mod.cmd_setup(SimpleNamespace())
    assert rc == 0
    cfg = patch_base.store.saved_cfg
    assert cfg is not None
    assert cfg.sso_start_url.endswith("/start")
    assert cfg.sso_region == "us-east-1"
    assert cfg.default_cli_region == "us-east-1"
    assert cfg.profile_naming == "{account_id}-{role_name}"


def test_perform_sso_login_updates_state_no_browser(patch_base):
    cfg = patch_base.store.load_config()
    access_token = cli_mod.perform_sso_login(cfg, patch_base.store, open_browser=False)
    assert access_token == "AT"
    st = patch_base.store.load_state()
    assert st.access_token == "AT"
    assert st.refresh_token == "RT"
    assert st.oidc_client_id == "cid"


def test_ensure_aws_config_calls_writer(patch_base, monkeypatch):
    # run selection to populate last profile name
    cfg = patch_base.store.load_config()
    access_token = cli_mod.perform_sso_login(cfg, patch_base.store, open_browser=False)
    # provide selections for account and role
    inputs = iter(["1", "1"])  # choose first account and first role
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(inputs))
    acc_id, role, profile = cli_mod.run_selection(cfg, patch_base.store, access_token)
    # ensure aws config
    cli_mod.ensure_aws_config(profile, cfg.default_cli_region, acc_id, role)


def test_login_failure(monkeypatch, patch_base, capsys):
    # Replace SsoClient with erroring client to trigger error path
    monkeypatch.setattr(cli_mod, "SsoClient", lambda *a, **k: DummySsoErr())
    rc = cli_mod.cmd_login(SimpleNamespace())
    assert rc == 1
    out = capsys.readouterr().out
    assert "Login failed:" in out


def test_credential_process_refresh_path(patch_base, capsys):
    # Expire access token and ensure refresh token path is used
    st = patch_base.store.load_state()
    st.last_account_id = "111111111111"
    st.last_role_name = "Admin"
    st.access_token = "OLD"
    st.access_token_expires_at = 0
    st.refresh_token = "RT"
    st.oidc_client_id = "cid"
    st.oidc_client_secret = "csec"
    st.oidc_client_secret_expires_at = 9999999999
    patch_base.store.save_state(st)

    cfg = patch_base.store.load_config()
    rc = cli_mod.credential_process_mode(cfg, patch_base.store, None, None)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["AccessKeyId"].startswith("AKIA")


def test_credential_process_missing_selection_returns_error(patch_base, capsys):
    # Clear state
    patch_base.store.state = {}
    cfg = patch_base.store.load_config()
    rc = cli_mod.credential_process_mode(cfg, patch_base.store, None, None)
    assert rc == 1
    err = json.loads(capsys.readouterr().out)
    assert err["Error"] == "No account/role available"


def test_credential_process_missing_config_returns_error(patch_base, capsys):
    # Simulate missing SSO config
    patch_base.store.saved_cfg = None
    # Monkeypatch load_config to return empty
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(cli_mod, "ConfigStore", lambda: patch_base.store)
    empty_cfg = cli_mod.ToolConfig()
    monkeypatch.setattr(patch_base.store, "load_config", lambda: empty_cfg)
    st = patch_base.store.load_state()
    st.last_account_id = "111111111111"
    st.last_role_name = "Admin"
    patch_base.store.save_state(st)
    rc = cli_mod.credential_process_mode(empty_cfg, patch_base.store, None, None)
    assert rc == 1
    err = json.loads(capsys.readouterr().out)
    assert err["Error"] == "SSO not configured"
    monkeypatch.undo()


def test_refresh_prints_export_when_profile_known(patch_base, capsys):
    st = patch_base.store.load_state()
    st.last_account_id = "111111111111"
    st.last_role_name = "Admin"
    st.last_profile_name = "Dev-111111111111-Admin"
    patch_base.store.save_state(st)

    rc = cli_mod.cmd_refresh(SimpleNamespace())
    assert rc == 0
    out = capsys.readouterr().out
    assert "export AWS_PROFILE=Dev-111111111111-Admin" in out
