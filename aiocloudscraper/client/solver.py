import re
from collections import OrderedDict
from html import unescape

from httpx import URL

from aiocloudscraper.client.resp_parser import detect_captcha_type, get_challenge_form, get_payload
from aiocloudscraper.interpreters import JavaScriptInterpreter
from aiocloudscraper.solvers.base import AbstractCaptchaSolver
from aiocloudscraper.types import CaptchaResult, CaptchaTypes


async def interpreter_solver(interpreter: JavaScriptInterpreter, body: str, url: URL) -> CaptchaResult:
    challenge = get_challenge_form(body, True)

    payload = OrderedDict()
    for challenge_param in re.findall(r"^\s*<input\s(.*?)/>", challenge.form, re.M | re.S):
        inputPayload = dict(re.findall(r'(\S+)="(\S+)"', challenge_param))
        if inputPayload.get("name") in ["r", "jschl_vc", "pass"]:
            payload.update({inputPayload["name"]: inputPayload["value"]})

    try:
        payload["jschl_answer"] = interpreter.solve_challenge(body, url.netloc)
    except Exception as e:
        raise Exception(
            f"Unable to parse Cloudflare anti-bots page: {getattr(e, 'message', e)}",
        )

    return CaptchaResult(
        url=f"{url.scheme}://{url.netloc}{unescape(challenge.challengeUUID)}",
        data=payload,
    )


async def third_party_solver(interpreter: AbstractCaptchaSolver, body: str, url: URL) -> CaptchaResult:
    challenge = get_challenge_form(body, False)
    payload = get_payload(challenge)
    captcha_type = detect_captcha_type(payload)
    captcha_response = await interpreter.solve_captcha(captcha_type, url)
    data_payload = OrderedDict(
        [
            ("r", payload.get('name="r" value', "")),
            ("cf_captcha_kind", payload['name="cf_captcha_kind" value']),
            ("id", payload.get("data-ray")),
            ("g-recaptcha-response", captcha_response),
        ]
    )

    if captcha_type == CaptchaTypes.H_CAPTCHA:
        payload.update({"h-captcha-response": captcha_response})

    return CaptchaResult(
        url=f"{url.scheme}://{url.netloc}{unescape(challenge.challengeUUID)}",
        data=data_payload,
    )
