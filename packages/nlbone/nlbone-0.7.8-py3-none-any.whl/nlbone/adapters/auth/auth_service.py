import requests

from nlbone.config.settings import get_settings
from nlbone.core.ports.auth import AuthService as BaseAuthService
from nlbone.utils.http import normalize_https_base


class AuthService(BaseAuthService):
    def __init__(self):
        s = get_settings()
        self._base_url = normalize_https_base(s.AUTH_SERVICE_URL.unicode_string())
        self._timeout = float(s.HTTP_TIMEOUT_SECONDS)
        self._client =  requests.session()

    def has_access(self, token: str, permissions: list[str]) -> bool: ...
    def verify_token(self, token: str) -> dict | None:
        url = f"{self._base_url}/introspect"
        result = self._client.post(url, data={
            "token": token
        })
        return result.json()
    def get_client_token(self) -> dict | None: ...
    def is_client_token(self, token: str, allowed_clients: set[str] | None = None) -> bool: ...
    def client_has_access(self, token: str, perms: list[str], allowed_clients: set[str] | None = None) -> bool: ...
    def get_permissions(self, token: str) -> list[str]: ...