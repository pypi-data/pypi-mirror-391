import json
import zlib
import base64
import sys
import time
import uuid
import os
import requests
from typing import Dict, Any, Optional


def to_unicode(x):
    if isinstance(x, bytes):
        return x.decode("utf-8")
    else:
        return str(x)


class ConfigError(Exception):
    """Raised for issues loading or parsing configuration."""

    pass


class TriggerError(Exception):
    """Raised when the event trigger request fails."""

    pass


def _get_gha_jwt(audience: str):
    if (
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN" in os.environ
        and "ACTIONS_ID_TOKEN_REQUEST_URL" in os.environ
    ):
        try:
            response = requests.get(
                url=os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"],
                headers={
                    "Authorization": f"Bearer {os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']}"
                },
                params={"audience": audience},
            )
            response.raise_for_status()
            return response.json()["value"]
        except Exception as e:
            raise ConfigError(
                f"Failed to fetch JWT token from GitHub Actions: {str(e)}"
            )

    raise ConfigError(
        "GHA flag was set, but $ACTIONS_ID_TOKEN_REQUEST_TOKEN and "
        "$ACTIONS_ID_TOKEN_REQUEST_URL env vars were not found."
    )


def _get_origin_token(
    service_principal_name: str,
    deployment: str,
    perimeter: str,
    token: str,
    auth_server: str,
):
    try:
        response = requests.get(
            f"{auth_server}/generate/service-principal",
            headers={"x-api-key": token},
            data=json.dumps(
                {
                    "servicePrincipalName": service_principal_name,
                    "deploymentName": deployment,
                    "perimeter": perimeter,
                }
            ),
        )
        response.raise_for_status()
        return response.json()["token"]
    except Exception as e:
        raise ConfigError(
            f"Failed to get origin token from {auth_server}. Error: {str(e)}"
        )


def _get_remote_metaflow_config_for_perimeter(
    origin_token: str, perimeter: str, api_server: str
):
    try:
        response = requests.get(
            f"{api_server}/v1/perimeters/{perimeter}/metaflowconfigs/default",
            headers={"x-api-key": origin_token},
        )
        response.raise_for_status()
        config = response.json()["config"]
        # The service principal auth key *is* the origin token.
        config["METAFLOW_SERVICE_AUTH_KEY"] = origin_token
        return config
    except Exception as e:
        raise ConfigError(
            f"Failed to get metaflow config from {api_server}. Error: {str(e)}"
        )


class EventTrigger:
    def __init__(self, name: str):
        self._name = name
        self._config: Dict[str, Any] = {}
        self._remote_config_pointer: Optional[Dict[str, Any]] = None
        self._initialized = False

    def _init_with_config_dict(self, config: dict):
        """Internal initializer that processes a config dict."""
        self._config = config

        # Check if this is a pointer to a remote config
        if self._config.get("OB_CONFIG_TYPE") == "aws-secrets-manager":
            self._remote_config_pointer = self._config
            # Load the remote config immediately
            try:
                self._refresh_remote_config()
            except Exception as e:
                raise ConfigError(f"Failed to load remote config on init: {e}")

        self._initialized = True

    def init(self, config_string: str = None, config_file_path: str = None):
        """
        Initializes the trigger with a static configuration.
        Provide either config_string or config_file_path.
        """
        config_dict = {}
        if config_string:
            try:
                config_dict = self._decode_config(config_string)
            except Exception as e:
                raise ConfigError(f"Failed to decode config string: {e}")
        elif config_file_path:
            try:
                with open(config_file_path, "r") as f:
                    config_dict = json.load(f)
            except Exception as e:
                raise ConfigError(f"Failed to read config file {config_file_path}: {e}")
        else:
            raise ConfigError("Must provide either config_string or config_file_path.")

        self._init_with_config_dict(config_dict)

    def init_from_service_principal(
        self,
        service_principal_name: str,
        deployment_domain: str,
        perimeter: str = "default",
        jwt_token: str = None,
        github_actions: bool = False,
    ):
        """
        Initializes the trigger by authenticating as a service principal.
        """
        # 1. Get IDP JWT
        audience = f"https://{deployment_domain}"
        if not jwt_token and github_actions:
            jwt_token = _get_gha_jwt(audience)

        if not jwt_token:
            raise ConfigError(
                "Must provide 'jwt_token' or set 'github_actions=True' in a GHA environment."
            )

        # 2. Exchange for Origin Token
        auth_server = f"https://auth.{deployment_domain}"
        deployment_name = deployment_domain.split(".")[0]
        origin_token = _get_origin_token(
            service_principal_name, deployment_name, perimeter, jwt_token, auth_server
        )

        # 3. Use Origin Token to get full Metaflow Config
        api_server = f"https://api.{deployment_domain}"
        metaflow_config = _get_remote_metaflow_config_for_perimeter(
            origin_token, perimeter, api_server
        )

        # 4. Create and initialize the instance
        self._init_with_config_dict(metaflow_config)

    def trigger(self, payload: dict):
        """
        Triggers the event with the given payload.
        """
        if not self._initialized:
            raise TriggerError(
                "EventTrigger has not been initialized. Call .init() first."
            )

        auth_key = self._config.get("METAFLOW_SERVICE_AUTH_KEY")
        if not auth_key:
            raise ConfigError("Config is missing 'METAFLOW_SERVICE_AUTH_KEY'.")

        # Refresh token if it's expired and we're using a remote config
        if self._remote_config_pointer and self._jwt_needs_refresh(auth_key):
            try:
                self._refresh_remote_config()
                auth_key = self._config["METAFLOW_SERVICE_AUTH_KEY"]
            except Exception as e:
                print(
                    f"Warning: Failed to refresh remote config/token. Error: {e}",
                    file=sys.stderr,
                )

        webhook_url = self._config.get("METAFLOW_ARGO_EVENTS_WEBHOOK_URL")
        if not webhook_url:
            raise ConfigError("Config is missing 'METAFLOW_ARGO_EVENTS_WEBHOOK_URL'.")

        # Build the final body
        body = {
            "payload": {
                "name": self._name,
                "id": str(uuid.uuid4()),
                "timestamp": int(time.time()),
                "utc_date": time.strftime("%Y%m%d", time.gmtime()),
                "generated-by-metaflow": False,
                **payload,
            }
        }

        self._make_fetch_request(webhook_url, auth_key, body)

    def _make_fetch_request(self, url: str, api_key: str, body: dict):
        try:
            response = requests.post(
                url,
                json=body,
                headers={"x-api-key": api_key},
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            raise TriggerError(f"Failed to send request to {url}: {error_details}")

    def _decode_config(self, encoded_config: str) -> dict:
        data = encoded_config.split(":", maxsplit=1)[-1]

        compressed = base64.b64decode(data)
        uncompressed = zlib.decompress(compressed)
        return json.loads(to_unicode(uncompressed))

    def _jwt_needs_refresh(self, token: str) -> bool:
        try:
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
            payload = json.loads(payload_json)

            if "exp" not in payload:
                return False

            current_timestamp = int(time.time())
            return payload["exp"] < (current_timestamp + 300)  # 5 * 60 seconds

        except Exception:
            return False

    def _refresh_remote_config(self):
        if not self._remote_config_pointer:
            raise ConfigError("No remote config pointer found.")

        config_type = self._remote_config_pointer.get("OB_CONFIG_TYPE")
        if config_type != "aws-secrets-manager":
            raise ConfigError(f"Unknown remote config type: {config_type}")

        try:
            arn = self._remote_config_pointer["AWS_SECRETS_MANAGER_SECRET_ARN"]
            region = self._remote_config_pointer["AWS_SECRETS_MANAGER_REGION"]
        except KeyError as e:
            raise ConfigError(f"Remote config is missing required key: {e}")

        try:
            import boto3
        except ImportError:
            raise ImportError(
                "The 'boto3' package is required for AWS Secrets Manager config. "
                "Please install it (e.g., 'pip install ob-events[aws]')"
            )

        try:
            client = boto3.client("secretsmanager", region_name=region)
            response = client.get_secret_value(SecretId=arn)

            if "SecretBinary" in response:
                secret_data = response["SecretBinary"]
                if isinstance(secret_data, bytes):
                    self._config = json.loads(secret_data.decode("utf-8"))
                else:
                    self._config = json.loads(secret_data)
            elif "SecretString" in response:
                self._config = json.loads(response["SecretString"])
            else:
                raise ConfigError(
                    "AWS Secret Value contains neither SecretBinary nor SecretString."
                )

        except Exception as e:
            raise ConfigError(f"Failed to retrieve secret {arn} from AWS: {e}")
