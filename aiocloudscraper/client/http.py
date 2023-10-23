import typing
from copy import deepcopy

from fake_useragent import FakeUserAgent
from httpx import _types
from httpx._client import USE_CLIENT_DEFAULT, AsyncClient, UseClientDefault
from httpx._config import (
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT_CONFIG,
    Limits,
)
from httpx._models import Response
from httpx._transports.base import AsyncBaseTransport

from aiocloudscraper.client.resp_parser import analyze_response_text
from aiocloudscraper.client.solver import interpreter_solver
from aiocloudscraper.interpreters import JavaScriptInterpreter
from aiocloudscraper.solvers import AbstractCaptchaSolver
from aiocloudscraper.types import Browser, ChallengeStatus

from .transport import CfScrapeTransport


class Client(AsyncClient):
    def __init__(
        self,
        *,
        browser: Browser,
        solver: typing.Optional[AbstractCaptchaSolver] = None,
        interpreter: typing.Optional[JavaScriptInterpreter] = None,
        auth: typing.Optional[_types.AuthTypes] = None,
        cipher_suite: typing.Optional[str] = None,
        ecdh_curve: typing.Optional[str] = None,
        params: typing.Optional[_types.QueryParamTypes] = None,
        headers: typing.Optional[_types.HeaderTypes] = None,
        cookies: typing.Optional[_types.CookieTypes] = None,
        verify: _types.VerifyTypes = False,
        cert: typing.Optional[_types.CertTypes] = None,
        http1: bool = True,
        http2: bool = False,
        proxies: typing.Optional[_types.ProxiesTypes] = None,
        mounts: typing.Optional[typing.Mapping[str, AsyncBaseTransport]] = None,
        timeout: _types.TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: typing.Optional[
            typing.Mapping[str, typing.List[typing.Callable[..., typing.Any]]]
        ] = None,
        base_url: _types.URLTypes = "",
        transport: typing.Optional[AsyncBaseTransport] = None,
        app: typing.Optional[typing.Callable[..., typing.Any]] = None,
        trust_env: bool = True,
        default_encoding: typing.Union[str, typing.Callable[[bytes], str]] = "utf-8",
    ):
        self.solver = solver
        self.browser = browser
        self.ua = FakeUserAgent(self.browser.value.lower())
        transport = CfScrapeTransport(
            browser=Browser.CHROME, cipher_suite=cipher_suite, ecdh_curve=ecdh_curve
        )
        self.interpreter = interpreter

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
        self.rotate_useragent()

    async def request(
        self,
        method: str,
        url: _types.URLTypes,
        *,
        content: typing.Optional[_types.RequestContent] = None,
        data: typing.Optional[_types.RequestData] = None,
        files: typing.Optional[_types.RequestFiles] = None,
        json: typing.Optional[typing.Any] = None,
        params: typing.Optional[_types.QueryParamTypes] = None,
        headers: typing.Optional[_types.HeaderTypes] = None,
        cookies: typing.Optional[_types.CookieTypes] = None,
        auth: typing.Union[
            _types.AuthTypes, UseClientDefault, None
        ] = USE_CLIENT_DEFAULT,
        follow_redirects: typing.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: typing.Union[
            _types.TimeoutTypes, UseClientDefault
        ] = USE_CLIENT_DEFAULT,
        extensions: typing.Optional[_types.RequestExtensions] = None,
    ) -> Response:
        """
        Build and send a request.

        Equivalent to:

        ```python
        request = client.build_request(...)
        response = await client.send(request, ...)
        ```

        See `AsyncClient.build_request()`, `AsyncClient.send()`
        and [Merging of configuration][0] for how the various parameters
        are merged with client-level configuration.

        [0]: /advanced/#merging-of-configuration
        """
        request = self.build_request(
            method=method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )
        follow_redirects = True
        response = await self.send(
            request, auth=auth, follow_redirects=follow_redirects
        )
        if response.status_code == 200:
            return response

        challenge = analyze_response_text(response)
        match challenge:
            case ChallengeStatus.IUAM_V1 | ChallengeStatus.H_CAPTCHA_V1:
                if not self.interpreter:
                    raise Exception("no interpreter")

                result = await interpreter_solver(
                    self.interpreter, response.text, response.url
                )

            case ChallengeStatus.H_CAPTCHA_V2 | ChallengeStatus.RECAPTCHA:
                raise Exception("...")
            case ChallengeStatus.IUAM_V2:
                raise Exception("...")
            case ChallengeStatus.FIREWALL_BLOCKED:
                raise Exception("...")
            case ChallengeStatus.UNKNOWN | _:
                print(response.text)
                print(response.status_code)
                raise Exception("...")

        def update_attr(obj, name, newValue):
            try:
                obj[name].update(newValue)
                return obj[name]
            except (AttributeError, KeyError):
                obj[name] = {}
                obj[name].update(newValue)
                return obj[name]

        if not result:
            return response

        follow_redirects = False
        post_data = deepcopy(data)
        data = update_attr(post_data, "data", result.data)

        headers = request.headers
        headers.update(
            **{
                "Origin": f"{response.url.scheme}://{response.url.netloc}",
                "Referer": response.url,
            }
        )

        request = self.build_request(
            method="POST",
            url=result.url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )
        new_response = await self.send(
            request, auth=auth, follow_redirects=follow_redirects
        )

        if new_response.status_code == 400:
            raise Exception("Invalid challenge answer detected, Cloudflare broken?")
        return new_response

    def inject_useragent(self, user_agent: str):
        self.user_agent = user_agent
        self.headers.update({"User-Agent": self.user_agent})

    def rotate_useragent(self):
        self.inject_useragent(self.ua.random)
