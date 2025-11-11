from typing import Callable, Optional, Union

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from nlbone.adapters.auth.auth_service import AuthService

try:
    from dependency_injector import providers

    ProviderType = providers.Provider  # type: ignore
except Exception:
    ProviderType = object

from nlbone.core.ports.auth import AuthService as BaseAuthService


def _to_factory(auth: Union[BaseAuthService, Callable[[], BaseAuthService], ProviderType]):
    try:
        from dependency_injector import providers as _p  # type: ignore

        if isinstance(auth, _p.Provider):
            return auth
    except Exception:
        pass
    if callable(auth) and not hasattr(auth, "verify_token"):
        return auth
    return lambda: auth


def authenticate_admin_user(request, auth_service):
    token: Optional[str] = None
    authz = request.headers.get("Authorization")
    if authz:
        try:
            scheme, token = authz.split(" ", 1)
            if scheme.lower() != "bearer":
                token = None
        except ValueError:
            token = None

    if token:
        request.state.token = token
        try:
            service: BaseAuthService = auth_service()
            data = service.verify_token(token)
            if data:
                request.state.user_id = data.get("user_id")
        except Exception:
            pass

def authenticate_user(request):
    token = request.cookies.get("access_token") or request.cookies.get("j_token")

    if token:
        request.state.token = token
        try:
            service: BaseAuthService = AuthService()
            data = service.verify_token(token)
            if data:
                request.state.user_id = data.get("sub")
        except Exception:
            pass


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth: Union[BaseAuthService, Callable[[], BaseAuthService], ProviderType]):
        super().__init__(app)
        self._get_auth = _to_factory(auth)

    async def dispatch(self, request: Request, call_next):
        request.state.client_id = request.headers.get("X-Client-Id")
        request.state.user_id = None
        request.state.token = None
        if request.cookies.get("access_token"):
            authenticate_user(request)
        elif request.headers.get("Authorization"):
            authenticate_admin_user(request, auth_service=self._get_auth)

        return await call_next(request)
