# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Copyright [2025] The Jackson Laboratory

# @see https://github.com/TheJacksonLaboratory/geneweaver-client/blob/main/src/geneweaver/client/auth.py

import time
from typing import Any, Dict, Optional

import jwt
import requests
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from . import auth_settings

import json
from pathlib import Path

import typer

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    
def check_auth()-> Optional[str]:
    """Check if the user is authenticated.

    :returns: The access token if the user is authenticated, None otherwise.
    """
    try:
        access_token = get_access_token()
        if access_token is None:
            login()
            return get_access_token()

        if (access_token_expired(access_token)):
            login()
            return get_access_token()
        
        return access_token
        
    except Exception as e:
        print("Authentication error: ", str(e))
        login()
        return get_access_token()

def login() -> Optional[Dict[str, any]]:
    
    
    """Run the device authorization flow."""
    device_code_data = _get_device_code_data()
    _print_device_code_instructions(device_code_data)
    token_data: Optional[Dict[str, any]] = _poll_for_flow_completion(device_code_data)
    save_auth_token(token_data)
    return token_data

def get_id_token() -> Optional[str]:
    """Get the ID token from the authentication token file.

    :returns: The ID token.
    """
    return _get_token_data_value_or_none("id_token")


def get_access_token() -> Optional[str]:
    """Get the Access token from the authentication token file.

    :returns: The ID token.
    """
    token = _get_token_data_value_or_none("access_token")
    if access_token_expired(token):
        refresh_token()
        token = _get_token_data_value_or_none("access_token")
    return token


def _get_token_data_value_or_none(token_data_key: str) -> Optional[str]:
    token_data = get_auth_token()

    if token_data is None:
        return None

    return token_data.get(token_data_key)


def validate_token(token: str) -> None:
    """Verify the token and its precedence.

    :param token:
    """
    jwks_url = "https://{}/.well-known/jwks.json".format(auth_settings.AUTH_DOMAIN)
    issuer = "https://{}/".format(auth_settings.AUTH_DOMAIN)
    sv = AsymmetricSignatureVerifier(jwks_url)
    tv = TokenVerifier(
        signature_verifier=sv, issuer=issuer, audience=auth_settings.AUTH_CLIENT_ID
    )
    tv.verify(token)


def access_token_expired(access_token: str) -> bool:
    """Check if the access token is unexpired."""
    token_data = get_auth_token()
    try:
        jwt.decode(
            token_data["access_token"],
            algorithms=auth_settings.AUTH_ALGORITHMS,
            options={
                "verify_signature": False,
                "verify_exp": True,
            },
        )
        return False
    except jwt.ExpiredSignatureError:
        return True


def refresh_token() -> None:
    """Refresh the access token."""
    token_data = get_auth_token()
    refresh_token = token_data["refresh_token"]
    payload = {
        "grant_type": "refresh_token",
        "client_id": auth_settings.AUTH_CLIENT_ID,
        "refresh_token": refresh_token,
    }
    response = requests.post(
        "https://{}/oauth/token".format(auth_settings.AUTH_DOMAIN), data=payload
    )
    token_data = response.json()
    token_data["refresh_token"] = get_auth_token()["refresh_token"]
    save_auth_token(token_data)


def current_user(id_token: str) -> Dict[str, str]:
    """Get the current user from the ID token."""
    return jwt.decode(
        id_token,
        algorithms=auth_settings.AUTH_ALGORITHMS,
        options={"verify_signature": False},
    )


def _device_code_payload() -> Dict[str, str]:
    return {
        "client_id": auth_settings.AUTH_CLIENT_ID,
        "audience": auth_settings.AUTH_AUDIENCE,
        "scope": " ".join(auth_settings.AUTH_SCOPES),
    }


def _get_device_code_data() -> dict:
    device_code_response = requests.post(
        "https://{}/oauth/device/code".format(auth_settings.AUTH_DOMAIN),
        data=_device_code_payload(),
    )

    if device_code_response.status_code != 200:
        raise AuthenticationError("Error generating the device code")

    return device_code_response.json()


def _print_device_code_instructions(device_code_data: Dict[str, Any]) -> None:
    print(
        "1. On your computer or mobile device navigate to: ",
        device_code_data["verification_uri_complete"],
    )
    print("2. Enter the following code: ", device_code_data["user_code"])


def _token_payload(device_code: str) -> Dict[str, str]:
    return {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "scope": "offline_access",
        "client_id": auth_settings.AUTH_CLIENT_ID,
    }


def _poll_for_flow_completion(
    device_code_data: Dict[str, Any]
) -> Optional[Dict[str, any]]:
    authenticated = False
    token_data = None
    while not authenticated:
        token_response = requests.post(
            "https://{}/oauth/token".format(auth_settings.AUTH_DOMAIN),
            data=_token_payload(device_code_data["device_code"]),
        )

        token_data = token_response.json()
        if token_response.status_code == 200:
            print("Authenticated!")
            print("- Id Token: {}...".format(token_data["id_token"][:10]))
            validate_token(token_data["id_token"])
            authenticated = True
        elif token_data["error"] not in ("authorization_pending", "slow_down"):
            raise AuthenticationError(token_data["error_description"])
        else:
            time.sleep(device_code_data["interval"])

    return token_data



def get_config_dir() -> Path:
    """Get the path to the configuration directory.

    :returns: The path to the configuration directory.
    """
    return Path(typer.get_app_dir("pyjit"))


def get_config_file() -> Path:
    """Get the path to the configuration file.

    :returns: The path to the configuration file.
    """
    return get_config_dir() / "config.json"


def get_auth_token_file() -> Path:
    """Get the path to the authentication token file.

    :returns: The path to the authentication token file.
    """
    return get_config_dir() / "auth_token.json"


def get_auth_token() -> Optional[dict]:
    """Get the authentication token data from the authentication token file.

    :returns: The authentication token.
    """
    auth_token_file = get_auth_token_file()

    if not auth_token_file.is_file():
        return None

    with open(auth_token_file, "r") as f:
        token = json.load(f)

    return token


def save_auth_token(token: dict) -> None:
    """Save the authentication token to the authentication token file.

    :param token: The authentication token.
    """
    auth_token_file = get_auth_token_file()
    auth_token_file.parent.mkdir(parents=True, exist_ok=True)

    with open(auth_token_file, "w") as f:
        json.dump(token, f)