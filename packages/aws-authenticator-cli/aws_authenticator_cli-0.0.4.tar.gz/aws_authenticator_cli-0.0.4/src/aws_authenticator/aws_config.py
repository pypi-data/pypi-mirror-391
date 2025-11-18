"""
Utilities for interacting with ~/.aws/config and ~/.aws/credentials.
- Ensure a profile entry with credential_process pointing to our CLI.
- Optionally write temporary credentials (not default when using credential_process).
- Export AWS_PROFILE suggestion.

We keep parsing/writing simple and robust: use configparser to handle INI format safely.
"""
from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

AWS_DIR = Path.home() / ".aws"
AWS_CONFIG = AWS_DIR / "config"
AWS_CREDENTIALS = AWS_DIR / "credentials"


class AwsConfig:
    def __init__(self):
        AWS_DIR.mkdir(exist_ok=True)

    def read_config(self) -> ConfigParser:
        parser = ConfigParser()
        parser.read(AWS_CONFIG)
        return parser

    def write_config(self, parser: ConfigParser) -> None:
        with AWS_CONFIG.open("w", encoding="utf-8") as f:
            parser.write(f)

    def read_credentials(self) -> ConfigParser:
        parser = ConfigParser()
        parser.read(AWS_CREDENTIALS)
        return parser

    def write_credentials(self, parser: ConfigParser) -> None:
        with AWS_CREDENTIALS.open("w", encoding="utf-8") as f:
            parser.write(f)

    def ensure_profile_with_credential_process(
        self,
        profile_name: str,
        process_command: str,
        region: str | None = None,
    ) -> None:
        """
        Ensure ~/.aws/config has a [profile <name>] section with credential_process and region.
        """
        parser = self.read_config()
        section = f"profile {profile_name}"
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, "credential_process", process_command)
        if region:
            parser.set(section, "region", region)
        self.write_config(parser)

    def write_static_credentials(
        self,
        profile_name: str,
        access_key_id: str,
        secret_access_key: str,
        session_token: str,
    ) -> None:
        """
        Write short-lived credentials to ~/.aws/credentials.
        """
        parser = self.read_credentials()
        section = profile_name
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, "aws_access_key_id", access_key_id)
        parser.set(section, "aws_secret_access_key", secret_access_key)
        parser.set(section, "aws_session_token", session_token)
        self.write_credentials(parser)


def export_profile_env(profile_name: str) -> str:
    """
    Return a shell command line to export AWS_PROFILE.
    Caller can print and the user can eval it.
    """
    return f"export AWS_PROFILE={profile_name}"
