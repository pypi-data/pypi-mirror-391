from __future__ import annotations

from configparser import ConfigParser

from aws_authenticator import aws_config as aws_cfg_mod
from aws_authenticator import config as config_mod
from aws_authenticator.aws_config import AwsConfig, export_profile_env
from aws_authenticator.config import ConfigStore, LastState, ToolConfig, render_profile_name


def test_render_profile_name():
    name = render_profile_name(
        "{account_alias}-{account_id}-{role_name}",
        account_alias="Dev",
        account_id="123456789012",
        role_name="Admin",
    )
    assert name == "Dev-123456789012-Admin"


def test_config_store_save_and_load(tmp_path, monkeypatch):
    # Point config dir to tmp
    monkeypatch.setattr(config_mod, "_detect_config_dir", lambda: tmp_path)
    store = ConfigStore()

    # Save config
    cfg = ToolConfig(
        sso_start_url="https://org.awsapps.com/start",
        sso_region="eu-west-1",
        default_cli_region="eu-west-1",
        profile_naming="{account_alias}-{account_id}-{role_name}",
    )
    store.save_config(cfg)
    # Load and verify
    loaded = store.load_config()
    assert loaded.sso_start_url == cfg.sso_start_url
    assert loaded.sso_region == cfg.sso_region
    assert loaded.default_cli_region == cfg.default_cli_region
    assert loaded.profile_naming == cfg.profile_naming

    # Save state and load back
    st = LastState(
        last_account_id="123456789012",
        last_role_name="Admin",
        last_profile_name="Dev-123456789012-Admin",
        oidc_client_id="cid",
        oidc_client_secret="csec",
        oidc_client_secret_expires_at=999999999,
        access_token="AT",
        access_token_expires_at=999999999,
        refresh_token="RT",
    )
    store.save_state(st)
    loaded_st = store.load_state()
    for k in LastState.__annotations__.keys():
        assert getattr(loaded_st, k) == getattr(st, k)


def test_aws_config_profile_and_credentials(tmp_path, monkeypatch):
    # Redirect ~/.aws paths to tmp
    monkeypatch.setattr(aws_cfg_mod, "AWS_DIR", tmp_path)
    monkeypatch.setattr(aws_cfg_mod, "AWS_CONFIG", tmp_path / "config")
    monkeypatch.setattr(aws_cfg_mod, "AWS_CREDENTIALS", tmp_path / "credentials")

    ac = AwsConfig()
    ac.ensure_profile_with_credential_process(
        "Dev-123456789012-Admin",
        process_command="python -m aws_authenticator.cli --credential-process --account 123456789012 --role Admin",
        region="eu-west-1",
    )

    # Verify config was written correctly
    parser = ConfigParser()
    parser.read(tmp_path / "config")
    section = "profile Dev-123456789012-Admin"
    assert parser.has_section(section)
    assert parser.get(section, "credential_process").endswith("--role Admin")
    assert parser.get(section, "region") == "eu-west-1"

    # Write static credentials and verify
    ac.write_static_credentials(
        "Dev-123456789012-Admin",
        access_key_id="AKIA...",
        secret_access_key="SECRET",
        session_token="TOKEN",
    )
    creds = ConfigParser()
    creds.read(tmp_path / "credentials")
    assert creds.has_section("Dev-123456789012-Admin")
    assert creds.get("Dev-123456789012-Admin", "aws_access_key_id").startswith("AKIA")
    assert "SECRET" == creds.get("Dev-123456789012-Admin", "aws_secret_access_key")
    assert "TOKEN" == creds.get("Dev-123456789012-Admin", "aws_session_token")

    # Export helper
    assert export_profile_env("Dev-123456789012-Admin").startswith("export AWS_PROFILE=")
