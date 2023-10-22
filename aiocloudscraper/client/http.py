import typing

from fake_useragent import FakeUserAgent
from httpx import AsyncClient
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG, Limits
from httpx._transports.base import AsyncBaseTransport
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    QueryParamTypes,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)

from aiocloudscraper.solvers import AbstractCaptchaSolver


class Client(AsyncClient):
    def __init__(
        self,
        *,
        solver: typing.Optional[AbstractCaptchaSolver] = None,
        auth: typing.Optional[AuthTypes] = None,
        params: typing.Optional[QueryParamTypes] = None,
        headers: typing.Optional[HeaderTypes] = None,
        cookies: typing.Optional[CookieTypes] = None,
        verify: VerifyTypes = True,
        cert: typing.Optional[CertTypes] = None,
        http1: bool = True,
        http2: bool = False,
        proxies: typing.Optional[ProxiesTypes] = None,
        mounts: typing.Optional[typing.Mapping[str, AsyncBaseTransport]] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: typing.Optional[typing.Mapping[str, typing.List[typing.Callable[..., typing.Any]]]] = None,
        base_url: URLTypes = "",
        transport: typing.Optional[AsyncBaseTransport] = None,
        app: typing.Optional[typing.Callable[..., typing.Any]] = None,
        trust_env: bool = True,
        default_encoding: typing.Union[str, typing.Callable[[bytes], str]] = "utf-8",
    ):
        self.solver = solver
        self.ua = FakeUserAgent()
        self.user_agent = self.ua.random

        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            base_url=base_url,
            verify=verify,
            cert=cert,
            http2=http2,
            transport=transport,
            app=app,
            http1=http1,
            proxies=proxies,
            limits=limits,
            trust_env=trust_env,
            default_encoding=default_encoding,
            mounts=mounts,
        )

    def inject_useragent(self, user_agent: str):
        self.user_agent = user_agent

    def rotate_useragent(self):
        self.inject_useragent(self.ua.random)
