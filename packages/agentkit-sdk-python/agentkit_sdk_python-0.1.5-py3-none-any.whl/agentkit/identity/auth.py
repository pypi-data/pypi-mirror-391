import asyncio
import os
from functools import wraps
from typing import Any, Callable

from agentkit.utils.credential import get_credential_from_vefaas_iam
from agentkit.utils.ve_sign import ve_request


def requires_api_key(*, provider_name: str, into: str = "api_key"):
    """Decorator that fetches an API key before calling the decorated function.

    Args:
        provider_name: The credential provider name
        into: Parameter name to inject the API key into

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        def _get_api_key() -> str:
            access_key = os.getenv("VOLCENGINE_ACCESS_KEY")
            secret_key = os.getenv("VOLCENGINE_SECRET_KEY")
            session_token = ""

            if not (access_key and secret_key):
                cred = get_credential_from_vefaas_iam()
                access_key = cred.access_key_id
                secret_key = cred.secret_access_key
                session_token = cred.session_token

            response = ve_request(
                request_body={
                    "ProviderName": provider_name,
                    "IdentityToken": "identity_token",
                },
                action="GetResourceApiKey",
                header={"X-Security-Token": session_token} if session_token else {},
                ak=access_key,
                sk=secret_key,
                version="2023-10-01",
                service="cis_test",
                host="open.volcengineapi.com",
                region="cn-beijing",
            )

            try:
                return response["Result"]["ApiKey"]
            except Exception as _:
                raise RuntimeError(f"Get api key failed: {response}")

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            api_key = _get_api_key()
            kwargs[into] = api_key
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            api_key = _get_api_key()
            kwargs[into] = api_key
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
