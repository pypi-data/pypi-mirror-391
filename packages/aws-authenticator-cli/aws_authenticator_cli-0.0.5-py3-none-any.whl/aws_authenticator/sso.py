"""
AWS SSO (IAM Identity Center) logic using boto3's sso-oidc and sso APIs.
Implements device authorization flow and retrieving role credentials.

References:
- RegisterClient: https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_RegisterClient.html
- StartDeviceAuthorization: https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_StartDeviceAuthorization.html
- CreateToken (poll): https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_CreateToken.html
- ListAccounts, ListAccountRoles, GetRoleCredentials: https://docs.aws.amazon.com/singlesignon/latest/APIReference/Welcome.html
"""
from __future__ import annotations

import time
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class SsoLoginError(Exception):
    pass


class SsoClient:
    def __init__(self, sso_region: str, start_url: str):
        self.sso_region = sso_region
        self.start_url = start_url
        self.oidc = boto3.client("sso-oidc", region_name=sso_region)
        self.sso = boto3.client("sso", region_name=sso_region)

    def device_authorization(self) -> dict[str, Any]:
        try:
            reg = self.oidc.register_client(
                clientName="aws-authenticator",
                clientType="public"
            )
            start = self.oidc.start_device_authorization(
                clientId=reg["clientId"],
                clientSecret=reg["clientSecret"],
                startUrl=self.start_url
            )
            return {**reg, **start}
        except (BotoCoreError, ClientError) as e:
            raise SsoLoginError(f"Failed to start device authorization: {e}")

    def wait_for_token(self, client_id: str, client_secret: str, device_code: str, interval: int, expires_in: int) -> dict[str, Any]:
        deadline = time.time() + expires_in
        while time.time() < deadline:
            try:
                token = self.oidc.create_token(
                    grantType="urn:ietf:params:oauth:grant-type:device_code",
                    deviceCode=device_code,
                    clientId=client_id,
                    clientSecret=client_secret,
                )
                return token
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code")
                if code in ("AuthorizationPendingException", "SlowDownException"):
                    time.sleep(interval)
                    continue
                raise SsoLoginError(f"Failed to create token: {e}")
        raise SsoLoginError("Device authorization expired before confirmation")

    def refresh_access_token(self, client_id: str, client_secret: str, refresh_token: str) -> dict[str, Any]:
        """
        Use refresh_token grant to obtain a new access token.
        """
        try:
            token = self.oidc.create_token(
                grantType="refresh_token",
                refreshToken=refresh_token,
                clientId=client_id,
                clientSecret=client_secret,
            )
            return token
        except (BotoCoreError, ClientError) as e:
            raise SsoLoginError(f"Failed to refresh access token: {e}")

    def list_accounts(self, access_token: str) -> list[dict[str, Any]]:
        accounts: list[dict[str, Any]] = []
        token = None
        while True:
            resp = self.sso.list_accounts(accessToken=access_token, nextToken=token) if token else self.sso.list_accounts(accessToken=access_token)
            accounts.extend(resp.get("accountList", []))
            token = resp.get("nextToken")
            if not token:
                break
        return accounts

    def list_account_roles(self, access_token: str, account_id: str) -> list[dict[str, Any]]:
        roles: list[dict[str, Any]] = []
        token = None
        while True:
            resp = self.sso.list_account_roles(accessToken=access_token, accountId=account_id, nextToken=token) if token else self.sso.list_account_roles(accessToken=access_token, accountId=account_id)
            roles.extend(resp.get("roleList", []))
            token = resp.get("nextToken")
            if not token:
                break
        return roles

    def get_role_credentials(self, access_token: str, account_id: str, role_name: str) -> dict[str, Any]:
        resp = self.sso.get_role_credentials(accessToken=access_token, accountId=account_id, roleName=role_name)
        return resp["roleCredentials"]
