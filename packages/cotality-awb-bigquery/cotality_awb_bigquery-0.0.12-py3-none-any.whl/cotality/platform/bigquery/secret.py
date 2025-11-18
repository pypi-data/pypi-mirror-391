# Copyright 2025 Cotality
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Google Secret Manager client implementation."""
from __future__ import annotations

import json
import logging
from typing import Optional

from google.api_core import exceptions as google_exceptions
from google.cloud import secretmanager
from google.oauth2 import service_account

from ...core.error_codes import CommonErrorCodes
from ...core.exception import ClgxException
from ...core.interfaces.secret import SecretClient as SecretInterface

logger = logging.getLogger(__name__)


class SecretClient(SecretInterface):
    """
    Google Secret Manager implementation for the SecretClient interface.

    This client interacts with Google Cloud Secret Manager to store and retrieve
    sensitive information like credentials.
    """

    # Define constants for secret names to ensure consistency
    _DG_API_SECRET_ID = "cotality_api_secret"
    _DG_USERNAME_SECRET_ID = "username"
    _DG_PW_SECRET_ID = "password"

    def __init__(self, project_id: str, credential_key: Optional[dict] = None) -> None:
        """
        Initialize the Google Secret Manager client.

        Args:
            project_id (str): Your Google Cloud project ID.
        """
        if not project_id:
            raise ValueError("Google Cloud project_id is required.")

        logger.info(
            "Initializing Google Secret Manager client. Project ID: %s", project_id
        )

        self._project_id = project_id
        if credential_key:
            credentials = service_account.Credentials.from_service_account_info(
                credential_key
            )
            self._client = secretmanager.SecretManagerServiceClient(
                credentials=credentials
            )
        else:
            self._client = secretmanager.SecretManagerServiceClient()

    def get_digital_gateway_credential(self) -> tuple[str, str]:
        """
        Return username & password for Digital Gateway from Google Secret Manager.

        Raises:
            ClgxException: If credentials cannot be retrieved.

        Returns:
            Tuple[str,str]: username, password
        """
        logger.info("Retrieving Digital Gateway credentials from Secret Manager.")
        username = ""
        password = ""
        try:
            secret = self._get_secret(self._DG_API_SECRET_ID)
            secret_json = json.loads(secret)
            username = secret_json.get("username")
            password = secret_json.get("password")
        except ClgxException as err:
            logger.error("Error retrieving Digital Gateway credentials: %s", err)
        return username, password

    def save_digital_gateway_credential(self, username: str, password: str) -> None:
        """
        Save the Digital Gateway credential to Google Secret Manager.

        Args:
            username (str): Username for Digital Gateway.
            password (str): Password for Digital Gateway.

        Raises:
            ClgxException: If credentials cannot be saved.
        """
        if not username or not password:
            raise ValueError("Username and password cannot be empty.")

        logger.info("Saving Digital Gateway credentials to Secret Manager.")

        api_values = {}
        api_values[self._DG_USERNAME_SECRET_ID] = username
        api_values[self._DG_PW_SECRET_ID] = password

        parent = f"projects/{self._project_id}"
        secret_name = f"{parent}/secrets/{self._DG_API_SECRET_ID}"

        try:
            payload = json.dumps(api_values).encode("UTF-8")
            self._client.add_secret_version(
                request={"parent": secret_name, "payload": {"data": payload}}
            )
            logger.info("Successfully saved new version for secrets!")
        except google_exceptions.PermissionDenied as err:
            raise ClgxException(
                error=CommonErrorCodes.GEN_PERMISSION_DENIED,
                parameters={"name": self._DG_API_SECRET_ID},
                message=f"Permission denied for fetch secret: {self._DG_API_SECRET_ID}",
                cause=err,
            ) from err
        except Exception as err:
            raise ClgxException(
                error=CommonErrorCodes.GEN_RUN_TIME,
                message=f"Failed to access secret: {self._DG_API_SECRET_ID}",
                cause=err,
            ) from err

    # == Private Methods ===
    def _get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Helper function to retrieve a secret's value.

        Args:
            secret_id (str): The ID of the secret.
            version (str, optional): The version of the secret. Defaults to "latest".

        Returns:
            str: The secret value as a string.

        Raises:
            ClgxException: If the secret cannot be accessed or does not exist.
        """
        name = self._client.secret_version_path(self._project_id, secret_id, version)
        try:
            response = self._client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except google_exceptions.NotFound as err:
            raise ClgxException(
                error=CommonErrorCodes.GEN_INVALID_PARAMETER,
                parameters={"name": secret_id},
                message=f"Secret not found: {secret_id}",
                cause=err,
            ) from err
        except google_exceptions.PermissionDenied as err:
            raise ClgxException(
                error=CommonErrorCodes.GEN_PERMISSION_DENIED,
                parameters={"name": secret_id},
                message=f"Permission denied for fetch secret: {secret_id}",
                cause=err,
            ) from err
        except Exception as err:
            raise ClgxException(
                error=CommonErrorCodes.GEN_RUN_TIME,
                message=f"Failed to access secret: {secret_id}",
                cause=err,
            ) from err
