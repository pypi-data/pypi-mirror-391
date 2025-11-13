import os
from types import TracebackType
from typing import Any, Dict, List, Optional

import httpx
from httpx import Response
from httpx._types import RequestFiles
from pydantic import BaseModel, ConfigDict
from typing_extensions import Type

from simba_sdk.config import MIDDLEWARE, Settings
from simba_sdk.core.requests.auth.token_store import BaseTokenStore
from simba_sdk.core.requests.exception import RequestException
from simba_sdk.core.requests.middleware.manager import MiddlewareManager

_PREFIX = "field_"


class SDKBase(BaseModel):
    """
    Base model for all SDK codegen models.

    We want to define the model_dump() behaviour as written.

    In addition, because the SDK mangles the proper field name during generation
    from OpenApi aliases (e.g., it maps an alias `@context` ->  field_context)
    because `@context` is not a valid python/pydantic field name.
    We take advantage of this BaseModel override to apply fix this so that
    despite the model defining, e.g. vc.field_context we acan stillacces it as vc.context.
    """

    # Keep your global config + dump defaults if you like
    model_config = ConfigDict(populate_by_name=True)

    def model_dump(self, *args, **kwargs):
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump_json(*args, **kwargs)

    # --- Read-only aliasing for 'field_'-prefixed fields ---
    def __getattr__(self, name: str) -> Any:
        """
        Read-only aliasing: only __getattr__ is overridden.
        If a real un-prefixed field exists (e.g. 'id'), it wins.
        Does not affect serialization; it's purely Python ergonomics.

        E.g. If 'context' is missing but 'field_context' exists as a model field,
        return that value. Only runs when normal attribute lookup fails
        since __getattr__ is only called when attribute access (getattr) fails.
        """
        mf = getattr(type(self), "model_fields", {})
        if name in mf:
            # There is a *real* model field named `name`, so missing attr
            # should raise as usual.
            raise AttributeError(name)

        pref = f"{_PREFIX}{name}"
        if pref in mf:
            # Use object.__getattribute__ to avoid recursion
            return object.__getattribute__(self, pref)

        raise AttributeError(name)

    def __dir__(self):
        """
        Ensure that the un-prefixed names (e.g. 'context' for 'field_context')
        also appear in dir() results for easier auto-completion.
        """
        base = set(super().__dir__())
        mf = getattr(type(self), "model_fields", {})
        synthetic = {
            k[len(_PREFIX) :]
            for k in mf
            if k.startswith(_PREFIX) and k[len(_PREFIX) :] not in mf
        }
        return sorted(base | synthetic)


class Client:
    def __init__(
        self,
        name: str,
        token_store: BaseTokenStore,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        client: Optional[httpx.AsyncClient] = None,
        timeout: Optional[float] = 100.0,
        middleware: Optional[List[str]] = None,
        settings: Optional[Settings] = None,
    ):
        self.name = name
        # TODO: BLK-6440 make settings vars kwargs
        self.settings = settings or Settings(**os.environ)
        self._client: httpx.AsyncClient = (
            httpx.AsyncClient(headers=headers, cookies=cookies, timeout=timeout)
            if not client
            else client
        )
        self.token_store = token_store
        self._authorised = False

        self.middleware_manager = MiddlewareManager()
        if middleware is not None:
            for ware in middleware:
                middleware_instance = MIDDLEWARE[ware]()
                middleware_instance.client = self._client
                self.middleware_manager.add_middleware(middleware_instance)
        else:
            for ware in MIDDLEWARE.keys():
                middleware_instance = MIDDLEWARE[ware]()
                middleware_instance.client = self._client
                self.middleware_manager.add_middleware(middleware_instance)

    async def __aenter__(self) -> "Client":
        await self._client.__aenter__()  # type: ignore
        return self

    async def __aexit__(
        self,
        exc_type: Type[Exception],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._client.__aexit__(exc_type, exc_val, exc_tb)  # type: ignore

    def build_url(self, url: str) -> str:
        if not url.startswith("/"):
            url = "/" + url

        return self.settings.base_url.format(self.name) + url

    def _get_token(self) -> Optional[str]:
        if self.token_store:
            token: Optional[str] = self.token_store.get_token(self.settings.client_id)
            return token
        raise LookupError("No token_path store registered to this client")

    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Response:
        return await self.send(
            "GET", url, params=params, headers=headers, cookies=cookies
        )

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, str]] = None,
        upload_file: Optional[RequestFiles] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Response:
        if not upload_file and not data:
            raise RequestException(
                status_code=400,
                message="Post requests must either send an upload_file or data.",
            )
        return await self.send(
            "POST",
            url,
            data=data,
            upload_file=upload_file,
            params=params,
            headers=headers,
            cookies=cookies,
        )

    async def put(
        self,
        url: str,
        data: Optional[Dict[str, str]] = None,
        upload_file: Optional[RequestFiles] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Response:
        return await self.send(
            "PUT",
            url,
            data=data,
            upload_file=upload_file,
            params=params,
            headers=headers,
            cookies=cookies,
        )

    async def patch(
        self,
        url: str,
        data: Optional[Dict[str, str]] = None,
        upload_file: Optional[RequestFiles] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Response:
        return await self.send(
            "PATCH",
            url,
            data=data,
            upload_file=upload_file,
            params=params,
            headers=headers,
            cookies=cookies,
        )

    async def delete(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Response:
        return await self.send(
            "DELETE", url, params=params, headers=headers, cookies=cookies
        )

    async def send(
        self,
        method: str,
        url: str,
        data: Optional[Dict] = None,
        upload_file: Optional[RequestFiles] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Response:
        """
        Send a request via the MiddlewareManager
        """
        await self.authorise(headers=headers)
        if data is None:
            data = {}
        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        if params is None:
            params = {}

        token = self._get_token()
        if token:
            headers = {"Authorization": f"Bearer {token}"}

        request = self._client.build_request(
            method,
            self.build_url(url),
            data=data if not isinstance(data, dict) else None,
            json=data if isinstance(data, dict) else None,
            files=upload_file,
            params=params,
            headers=headers,
            cookies=cookies,
        )
        resp: Response = await self.middleware_manager.send(
            request, self._client._transport
        )
        if resp.status_code >= 300:
            try:
                error = resp.json()["detail"]
            except (KeyError, AttributeError):
                error = resp.text
            raise RequestException(
                status_code=resp.status_code,
                message=f"Request was unsuccessful: {error}",
            )
        return resp

    async def authorise(
        self, token_url: Optional[str] = None, headers: Optional[Dict] = None
    ) -> None:
        """
        Get an auth token_path via client credentials and store
        """
        if not self.token_store:
            raise LookupError("No token store registered to this client")
        if self._authorised and not self.token_store.is_expired_token(
            self.settings.client_id
        ):
            return
        # We need to authorise, set False until we do that successfully
        self._authorised = False
        if not token_url:
            token_url = self.settings.token_url
        if headers is None:
            headers = {}
        request = self._client.build_request(
            "POST",
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.settings.client_id,
                "client_secret": self.settings.client_secret,
            },
            headers=headers,
        )
        resp: Response = await self.middleware_manager.send(
            request, self._client._transport
        )
        if not resp.status_code == 200:
            raise RequestException(
                status_code=resp.status_code,
                message=f"Authorization failed: {resp.text}",
            )
        resp_json = resp.json()
        self.token_store.set_token(
            identifier=self.settings.client_id,
            token=resp_json["access_token"],
            expires=resp_json["expires_at"],
        )
        self._authorised = True
