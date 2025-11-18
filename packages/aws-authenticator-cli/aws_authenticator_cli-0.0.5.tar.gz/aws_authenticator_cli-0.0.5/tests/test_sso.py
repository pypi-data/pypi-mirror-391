from __future__ import annotations

import types

import pytest

from aws_authenticator.sso import SsoClient, SsoLoginError


class FakeBotoClient:
    def __init__(self, kind, behavior):
        self.kind = kind
        self.behavior = behavior

    # sso-oidc methods
    def register_client(self, clientName, clientType):
        return self.behavior["register_client"]

    def start_device_authorization(self, clientId, clientSecret, startUrl):
        return self.behavior["start_device_authorization"]

    def create_token(self, **kwargs):
        return self.behavior["create_token"](kwargs)

    # sso methods
    def list_accounts(self, **kwargs):
        return self.behavior["list_accounts"](kwargs)

    def list_account_roles(self, **kwargs):
        return self.behavior["list_account_roles"](kwargs)

    def get_role_credentials(self, **kwargs):
        return self.behavior["get_role_credentials"](kwargs)


class ClientErrorEx(Exception):
    def __init__(self, code):
        self.response = {"Error": {"Code": code}}


@pytest.fixture
def patch_boto3(monkeypatch):
    behavior = {
        "register_client": {"clientId": "cid", "clientSecret": "csec"},
        "start_device_authorization": {"deviceCode": "dcode", "interval": 0, "expiresIn": 5, "verificationUri": "http://v"},
    }

    def make_client(service_name, region_name=None):
        return FakeBotoClient(service_name, behavior)

    import aws_authenticator.sso as sso_mod
    monkeypatch.setattr(sso_mod, "boto3", types.SimpleNamespace(client=make_client))
    monkeypatch.setattr(sso_mod, "ClientError", ClientErrorEx)
    monkeypatch.setattr(sso_mod, "BotoCoreError", Exception)
    return behavior


def test_device_authorization_and_wait_success(patch_boto3):
    behavior = patch_boto3
    # create_token returns token immediately
    behavior["create_token"] = lambda kwargs: {"accessToken": "AT", "expiresIn": 600}

    client = SsoClient("eu-west-1", "http://start")
    reg_and_start = client.device_authorization()
    assert reg_and_start["clientId"] == "cid"
    token = client.wait_for_token("cid", "csec", "dcode", interval=0, expires_in=1)
    assert token["accessToken"] == "AT"


def test_wait_for_token_authorization_pending(monkeypatch, patch_boto3):
    behavior = patch_boto3
    # First call raises pending, second returns token
    calls = {"n": 0}

    def ct(kwargs):
        if calls["n"] == 0:
            calls["n"] += 1
            raise ClientErrorEx("AuthorizationPendingException")
        return {"accessToken": "AT", "expiresIn": 600}

    behavior["create_token"] = ct
    client = SsoClient("eu-west-1", "http://start")
    token = client.wait_for_token("cid", "csec", "dcode", interval=0, expires_in=2)
    assert token["accessToken"] == "AT"


def test_wait_for_token_expired(monkeypatch, patch_boto3):
    behavior = patch_boto3

    def ct(kwargs):
        raise ClientErrorEx("AuthorizationPendingException")

    behavior["create_token"] = ct
    client = SsoClient("eu-west-1", "http://start")
    with pytest.raises(SsoLoginError):
        client.wait_for_token("cid", "csec", "dcode", interval=0, expires_in=0)


def test_refresh_access_token_error(monkeypatch, patch_boto3):
    behavior = patch_boto3

    def ct(kwargs):
        raise ClientErrorEx("OtherError")

    behavior["create_token"] = ct
    client = SsoClient("eu-west-1", "http://start")
    with pytest.raises(SsoLoginError):
        client.refresh_access_token("cid", "csec", "RT")


def test_list_accounts_and_roles_and_get_creds(monkeypatch, patch_boto3):
    behavior = patch_boto3

    def list_accounts(kwargs):
        if "nextToken" in kwargs:
            return {"accountList": [{"accountId": "b", "accountName": "B"}]}
        return {"accountList": [{"accountId": "a", "accountName": "A"}], "nextToken": "t"}

    behavior["list_accounts"] = list_accounts

    def list_roles(kwargs):
        if "nextToken" in kwargs:
            return {"roleList": [{"roleName": "R2"}]}
        return {"roleList": [{"roleName": "R1"}], "nextToken": "t"}

    behavior["list_account_roles"] = list_roles

    def get_role_credentials(kwargs):
        return {"roleCredentials": {"accessKeyId": "AK", "secretAccessKey": "SK", "sessionToken": "ST"}}

    behavior["get_role_credentials"] = get_role_credentials

    client = SsoClient("eu-west-1", "http://start")
    accounts = client.list_accounts("AT")
    assert [a["accountId"] for a in accounts] == ["a", "b"]
    roles = client.list_account_roles("AT", "a")
    assert [r["roleName"] for r in roles] == ["R1", "R2"]
    creds = client.get_role_credentials("AT", "a", "R1")
    assert creds["accessKeyId"] == "AK"
