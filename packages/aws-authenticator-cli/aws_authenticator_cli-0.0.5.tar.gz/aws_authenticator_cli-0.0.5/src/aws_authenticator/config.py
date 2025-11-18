"""
Configuration management for aws-authenticator.
Stores tool-specific config in ~/.config/aws-authenticator/config.toml (on macOS/Linux)
- sso_start_url
- sso_region
- default_cli_region
- profile_naming: convention for profile names
Also tracks last used account_id and role_name for quick suggestion, and caches SSO tokens and OIDC client registration for refresh.

We intentionally avoid extra dependencies: use tomllib (Python 3.11+) or fallback to a minimal parser.
For Python 3.10, we include a lightweight TOML reader/writer via tomli (only if available) else fallback to JSON.

On macOS, config folder: ~/Library/Application Support/aws-authenticator
On Linux: ~/.config/aws-authenticator
On others: ~/.aws-authenticator
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import tomllib  # Python 3.11+
    _HAVE_TOMLLIB = True
except Exception:
    _HAVE_TOMLLIB = False
    try:
        import tomli as tomllib
        _HAVE_TOMLLIB = True
    except Exception:
        pass
    
CONFIG_DIR_MAC = Path.home() / "Library" / "Application Support" / "aws-authenticator"
CONFIG_DIR_LINUX = Path.home() / ".config" / "aws-authenticator"
CONFIG_DIR_OTHER = Path.home() / ".aws-authenticator"

CONFIG_FILE_NAME = "config.toml"
STATE_FILE_NAME = "state.json"  # last-used selections, tokens metadata


def _detect_config_dir() -> Path:
    if sys.platform == "darwin":
        return CONFIG_DIR_MAC
    if sys.platform.startswith("linux"):
        return CONFIG_DIR_LINUX
    return CONFIG_DIR_OTHER


@dataclass
class ToolConfig:
    sso_start_url: str | None = None
    sso_region: str | None = None
    default_cli_region: str | None = None
    profile_naming: str = "{account_alias}-{account_id}-{role_name}"  # naming convention template

    def validate(self) -> None:
        # Validate placeholders in profile_naming
        for key in ["account_alias", "account_id", "role_name"]:
            if f"{{{key}}}" not in self.profile_naming:
                # allow but warn via print
                pass


@dataclass
class LastState:
    last_account_id: str | None = None
    last_role_name: str | None = None
    last_profile_name: str | None = None
    # OIDC client registration (from RegisterClient)
    oidc_client_id: str | None = None
    oidc_client_secret: str | None = None
    oidc_client_secret_expires_at: int | None = None  # epoch seconds
    # Token cache
    access_token: str | None = None
    access_token_expires_at: int | None = None  # epoch seconds
    refresh_token: str | None = None


class ConfigStore:
    def __init__(self):
        self.base_dir = _detect_config_dir()
        self.config_path = self.base_dir / CONFIG_FILE_NAME
        self.state_path = self.base_dir / STATE_FILE_NAME
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> ToolConfig:
        if self.config_path.exists():
            try:
                with self.config_path.open("rb") as f:
                    if _HAVE_TOMLLIB:
                        data = tomllib.load(f)
                    else:
                        # Fallback: try JSON
                        data = json.loads(f.read().decode("utf-8"))
            except Exception:
                data = {}
        else:
            data = {}
        return ToolConfig(
            sso_start_url=data.get("sso_start_url"),
            sso_region=data.get("sso_region"),
            default_cli_region=data.get("default_cli_region"),
            profile_naming=data.get("profile_naming", ToolConfig().profile_naming),
        )

    def save_config(self, cfg: ToolConfig) -> None:
        cfg.validate()
        content = (
            f"sso_start_url = \"{cfg.sso_start_url or ''}\"\n"
            f"sso_region = \"{cfg.sso_region or ''}\"\n"
            f"default_cli_region = \"{cfg.default_cli_region or ''}\"\n"
            f"profile_naming = \"{cfg.profile_naming}\"\n"
        )
        with self.config_path.open("wb") as f:
            f.write(content.encode("utf-8"))

    def load_state(self) -> LastState:
        if self.state_path.exists():
            try:
                with self.state_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        else:
            data = {}
        # Only keep known keys for forward/backward compatibility
        filtered = {k: data.get(k) for k in LastState.__annotations__.keys()}
        return LastState(**filtered)

    def save_state(self, state: LastState) -> None:
        with self.state_path.open("w", encoding="utf-8") as f:
            json.dump(asdict(state), f, indent=2)


def render_profile_name(template: str, account_alias: str, account_id: str, role_name: str) -> str:
    # Safe rendering: replace known placeholders, leave others untouched
    name = template
    name = name.replace("{account_alias}", account_alias)
    name = name.replace("{account_id}", account_id)
    name = name.replace("{role_name}", role_name)
    return name
