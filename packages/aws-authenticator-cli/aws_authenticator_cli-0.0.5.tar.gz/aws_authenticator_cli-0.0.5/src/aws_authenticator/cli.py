"""
CLI entry point for aws-authenticator.
Features:
- Reads tool config (sso_start_url, sso_region, default_cli_region, profile naming template).
- Runs device authorization flow and opens browser URL for AWS SSO.
- Lets user interactively pick account and role (suggest last used).
- Ensures ~/.aws/config has credential_process pointing to this CLI with selected account/role.
- Prints export AWS_PROFILE=... for convenience.
- Supports a `--credential-process` mode that outputs credentials JSON for AWS CLI.
- Supports a `refresh` command to re-login quickly.

Usage examples:
- aws-authenticator setup          # configure sso_start_url, sso_region, default_cli_region, naming
- aws-authenticator login          # web login + choose account/role + setup profile + export
- aws-authenticator --credential-process --account <id> --role <name>    # used by AWS CLI
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import webbrowser

from .aws_config import AwsConfig, export_profile_env
from .config import ConfigStore, LastState, ToolConfig, render_profile_name  # noqa: F401
from .sso import SsoClient, SsoLoginError

CREDENTIAL_PROCESS_OUTPUT_TEMPLATE = {
    "Version": 1,
    "AccessKeyId": "",
    "SecretAccessKey": "",
    "SessionToken": "",
    # Optional: seconds until expiration. AWS CLI can handle without, but we include for clarity.
    # "Expiration": "2020-01-01T00:00:00Z"
}


def _prompt(text: str, default: str | None = None) -> str:
    prompt = f"{text}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    val = input(prompt).strip()
    return val or (default or "")


def _select_from_list(title: str, items: list[tuple[str, str]], default_idx: int | None = None) -> tuple[str, str]:
    print(title)
    for idx, (key, label) in enumerate(items):
        marker = "*" if default_idx is not None and idx == default_idx else " "
        print(f"  {idx+1}. {label} {marker}")
    while True:
        choice = input("Select number: ").strip()
        if not choice and default_idx is not None:
            return items[default_idx]
        try:
            i = int(choice)
            if 1 <= i <= len(items):
                return items[i-1]
        except Exception:
            pass
        print("Invalid selection, try again.")


def perform_sso_login(cfg: ToolConfig, store: ConfigStore, open_browser: bool = True) -> str:
    if not cfg.sso_start_url or not cfg.sso_region:
        print("SSO start URL and region are not configured. Run 'aws-authenticator setup' first.")
        sys.exit(2)
    sso = SsoClient(cfg.sso_region, cfg.sso_start_url)
    auth = sso.device_authorization()
    if open_browser:
        print("Open the following URL in your browser and enter the provided code if prompted:")
        url = (auth.get("verificationUriComplete") or auth.get("verificationUri")) or ""
        print(url)
        try:
            if url:
                webbrowser.open(url)
        except Exception:
            pass
    token = sso.wait_for_token(
        client_id=auth["clientId"],
        client_secret=auth["clientSecret"],
        device_code=auth["deviceCode"],
        interval=auth["interval"],
        expires_in=auth["expiresIn"],
    )
    access_token = token["accessToken"]
    # Cache client and tokens
    expires_at = int(time.time()) + int(token.get("expiresIn", 0))
    last = store.load_state()
    last.oidc_client_id = auth.get("clientId")
    last.oidc_client_secret = auth.get("clientSecret")
    last.oidc_client_secret_expires_at = auth.get("clientSecretExpiresAt")
    last.access_token = access_token
    last.access_token_expires_at = expires_at
    # Some environments return refreshToken, cache if present
    if token.get("refreshToken"):
        last.refresh_token = token.get("refreshToken")
    store.save_state(last)
    return access_token


def run_selection(cfg: ToolConfig, store: ConfigStore, access_token: str) -> tuple[str, str, str]:
    assert cfg.sso_region is not None and cfg.sso_start_url is not None
    sso = SsoClient(cfg.sso_region, cfg.sso_start_url)
    accounts = sso.list_accounts(access_token)
    if not accounts:
        print("No accounts available for your SSO session.")
        sys.exit(3)
    items = []
    for a in accounts:
        label = f"{a.get('accountName','')} ({a['accountId']})"
        items.append((a["accountId"], label))
    last = store.load_state()
    default_idx = None
    if last.last_account_id:
        for i, (acc_id, _) in enumerate(items):
            if acc_id == last.last_account_id:
                default_idx = i
                break
    account_id, account_label = _select_from_list("Select AWS account:", items, default_idx)
    roles = sso.list_account_roles(access_token, account_id)
    if not roles:
        print("No roles available in selected account.")
        sys.exit(4)
    role_items = []
    for r in roles:
        role_items.append((r['roleName'], f"{r['roleName']}"))
    role_default_idx = None
    if last.last_role_name:
        for i, (rn, _) in enumerate(role_items):
            if rn == last.last_role_name:
                role_default_idx = i
                break
    role_name, _ = _select_from_list("Select role:", role_items, role_default_idx)
    account_alias = account_label.split("(")[0].strip()
    profile_name = render_profile_name(cfg.profile_naming, account_alias, account_id, role_name)
    # Save state
    last.last_account_id = account_id
    last.last_role_name = role_name
    last.last_profile_name = profile_name
    store.save_state(last)
    return account_id, role_name, profile_name


def ensure_aws_config(profile_name: str, region: str | None, account_id: str, role_name: str) -> None:
    proc_cmd = (
        f"{sys.executable} -m aws_authenticator.cli --credential-process "
        f"--account {account_id} --role {role_name}"
    )
    AwsConfig().ensure_profile_with_credential_process(profile_name, proc_cmd, region)


def credential_process_mode(cfg: ToolConfig, store: ConfigStore, account_override: str | None, role_override: str | None) -> int:
    """
    Entry point when invoked by AWS CLI via credential_process.
    Output JSON with credentials. Use profile-specific account/role if provided, else last selection.
    Reuse cached access token or refresh via refresh_token if available; do not open browser.
    """
    last = store.load_state()
    if not cfg.sso_start_url or not cfg.sso_region:
        print(json.dumps({"Version": 1, "Error": "SSO not configured"}))
        return 1
    account_id = account_override or last.last_account_id
    role_name = role_override or last.last_role_name
    if not account_id or not role_name:
        print(json.dumps({"Version": 1, "Error": "No account/role available"}))
        return 1

    sso = SsoClient(cfg.sso_region, cfg.sso_start_url)
    # Determine access token
    now = int(time.time())
    access_token = None
    if last.access_token and last.access_token_expires_at and last.access_token_expires_at - 60 > now:
        access_token = last.access_token
    elif last.refresh_token and last.oidc_client_id and last.oidc_client_secret and (not last.oidc_client_secret_expires_at or last.oidc_client_secret_expires_at > now):
        try:
            t = sso.refresh_access_token(last.oidc_client_id, last.oidc_client_secret, last.refresh_token)
            access_token = t.get("accessToken")
            last.access_token = access_token
            last.access_token_expires_at = now + int(t.get("expiresIn", 0))
            store.save_state(last)
        except SsoLoginError:
            print(json.dumps({"Version": 1, "Error": "AuthorizationRequired"}))
            return 1
    else:
        print(json.dumps({"Version": 1, "Error": "AuthorizationRequired"}))
        return 1

    assert access_token is not None
    creds = sso.get_role_credentials(access_token, account_id, role_name)
    out = {
        "Version": 1,
        "AccessKeyId": creds["accessKeyId"],
        "SecretAccessKey": creds["secretAccessKey"],
        "SessionToken": creds["sessionToken"],
    }
    print(json.dumps(out))
    return 0
    

def cmd_setup(args) -> int:
    store = ConfigStore()
    cfg = store.load_config()
    print("Configure AWS SSO settings. Leave empty to keep current value.")
    sso_start_url = _prompt("SSO start URL", cfg.sso_start_url)
    sso_region = _prompt("SSO region", cfg.sso_region)
    default_cli_region = _prompt("Default CLI region", cfg.default_cli_region)
    profile_naming = _prompt("Profile naming template", cfg.profile_naming)
    cfg = ToolConfig(
        sso_start_url=sso_start_url or None,
        sso_region=sso_region or None,
        default_cli_region=default_cli_region or None,
        profile_naming=profile_naming or cfg.profile_naming,
    )
    store.save_config(cfg)
    print("Saved configuration.")
    return 0


def cmd_login(args) -> int:
    store = ConfigStore()
    cfg = store.load_config()

    try:
        access_token = perform_sso_login(cfg, store, open_browser=True)
        account_id, role_name, profile_name = run_selection(cfg, store, access_token)
    except SsoLoginError as e:
        print(f"Login failed: {e}")
        return 1

    # Ensure aws config has credential_process for this profile (profile-specific account/role)
    ensure_aws_config(profile_name, cfg.default_cli_region, account_id, role_name)

    print(f"Configured AWS profile: {profile_name}")
    print("To use in current shell, run:")
    print(export_profile_env(profile_name))
    return 0


def cmd_refresh(args) -> int:
    """
    Quick refresh command: perform device authorization and update token cache without re-selecting.
    """
    store = ConfigStore()
    cfg = store.load_config()
    last = store.load_state()
    if not last.last_account_id or not last.last_role_name:
        print("No previous account/role selection. Run 'aws-authenticator login' first.")
        return 2
    try:
        perform_sso_login(cfg, store, open_browser=True)
    except SsoLoginError as e:
        print(f"Refresh failed: {e}")
        return 1
    print("Authentication refreshed.")
    if last.last_profile_name:
        print(export_profile_env(last.last_profile_name))
    else:
        print("Run 'aws-authenticator login' to regenerate profile name.")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aws-authenticator")
    p.add_argument("--credential-process", action="store_true", help="Run in credential_process mode (AWS CLI invokes this)")
    p.add_argument("--account", help="Account ID for credential_process mode", default=None)
    p.add_argument("--role", help="Role name for credential_process mode", default=None)
    sub = p.add_subparsers(dest="command")
    sub.add_parser("setup", help="Configure SSO settings")
    sub.add_parser("login", help="Authenticate and select account/role; configure AWS profile and print export")
    sub.add_parser("refresh", help="Refresh authentication quickly")
    return p


def main() -> None:
    p = build_arg_parser()
    args = p.parse_args()
    store = ConfigStore()
    cfg = store.load_config()

    if args.credential_process:
        rc = credential_process_mode(cfg, store, args.account, args.role)
        sys.exit(rc)
    
    if args.command == "setup":
        sys.exit(cmd_setup(args))
    elif args.command == "login":
        sys.exit(cmd_login(args))
    elif args.command == "refresh":
        sys.exit(cmd_refresh(args))
    else:
        p.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
