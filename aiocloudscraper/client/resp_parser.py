import re
from typing import OrderedDict

from httpx import Response

from aiocloudscraper.types import CaptchaTypes, ChallengeForm, ChallengeStatus


def get_server_header(resp: Response) -> str:
    return resp.headers.get("Server") or ""


def is_uiam(resp: Response) -> ChallengeStatus | None:
    """
    check if the response contains a valid UIAM Cloudflare challenge
    """
    server = get_server_header(resp)
    result = (
        server.startswith("cloudflare")
        and resp.status_code in [429, 503]
        and re.search(r"/cdn-cgi/images/trace/jsch/", resp.text, re.M | re.S)
        and re.search(
            r"""<form .*?="challenge-form" action="/\S+__cf_chl_f_tk=""",
            resp.text,
            re.M | re.S,
        )
    )

    return ChallengeStatus.IUAM_V1 if bool(result) else None


def is_new_uiam_challenge(resp: Response) -> ChallengeStatus | None:
    """
    check if the response contains a valid Cloudflare challenge
    """
    result = is_uiam(resp) and re.search(
        r"""cpo.src\s*=\s*['"]/cdn-cgi/challenge-platform/\S+orchestrate/jsch/v1""",
        resp.text,
        re.M | re.S,
    )
    return ChallengeStatus.IUAM_V2 if bool(result) else None


def is_h_captcha_v2_challenge(resp: Response) -> ChallengeStatus | None:
    """check if the response contains a v2 hCaptcha Cloudflare challenge"""
    result = is_uiam(resp) and re.search(
        r"""cpo.src\s*=\s*['"]/cdn-cgi/challenge-platform/\S+orchestrate/(captcha|managed)/v1""",
        resp.text,
        re.M | re.S,
    )
    return ChallengeStatus.H_CAPTCHA_V2 if bool(result) else None


def is_h_captcha_v1_challenge(resp: Response) -> ChallengeStatus | None:
    """check if the response contains a v2 hCaptcha Cloudflare challenge"""
    server = get_server_header(resp)
    result = (
        server.startswith("cloudflare")
        and re.search(
            r"/cdn-cgi/images/trace/(captcha|managed)/", resp.text, re.M | re.S
        )
        and re.search(
            r"""<form .*?="challenge-form" action="/\S+__cf_chl_f_tk=""",
            resp.text,
            re.M | re.S,
        )
    )
    return ChallengeStatus.H_CAPTCHA_V1 if bool(result) else None


def is_firewall_blocked(resp: Response) -> ChallengeStatus | None:
    """check if the response contains Firewall 1020 Error"""
    server = get_server_header(resp)
    result = (
        server.startswith("cloudflare")
        and resp.status_code == 403
        and re.search(
            r'<span class="cf-error-code">1020</span>', resp.text, re.M | re.DOTALL
        )
    )
    return ChallengeStatus.FIREWALL_BLOCKED if bool(result) else None


def analyze_response_text(resp: Response) -> ChallengeStatus:
    """
    Hook into cloudflare's response to see if it contains detected status
    if not, it return ChallengeStatus.UNKNOWN

    Args:
        resp (Response): Cloudflare Response
    """
    result = is_firewall_blocked(resp)
    result = result or is_firewall_blocked(resp)
    result = result or is_h_captcha_v1_challenge(resp)
    result = result or is_h_captcha_v2_challenge(resp)
    result = result or is_new_uiam_challenge(resp)
    result = result or is_uiam(resp)
    return result or ChallengeStatus.UNKNOWN


def get_challenge_form(body: str, is_um: bool) -> ChallengeForm:
    if is_um:
        challenge_form = re.search(
            r'<form (?P<form>.*?="challenge-form" '
            r'action="(?P<challengeUUID>.*?'
            r'__cf_chl_f_tk=\S+)"(.*?)</form>)',
            body,
            re.M | re.DOTALL,
        )

    else:
        challenge_form = re.search(
            r'<form (?P<form>.*?="challenge-form" '
            r'action="(?P<challengeUUID>.*?__cf_chl_captcha_tk__=\S+)"(.*?)</form>)',
            body,
            re.M | re.DOTALL,
        )

    if challenge_form is None:
        raise Exception(
            "Cloudflare Captcha detected, unfortunately we can't extract the parameters correctly."
        )

    form_payload = challenge_form.groupdict()
    if not all(key in form_payload for key in ["form", "challengeUUID"]):
        raise Exception(
            "Cloudflare Captcha detected, unfortunately we can't extract the parameters correctly."
        )
    return ChallengeForm(**form_payload)


def get_payload(challenge_form: ChallengeForm) -> dict:
    result = OrderedDict(
        re.findall(
            r'(name="r"\svalue|data-ray|data-sitekey|name="cf_captcha_kind"\svalue)="(.*?)"',
            challenge_form.form,
        )
    )
    return result


def detect_captcha_type(payload: dict) -> CaptchaTypes:
    """Attempts to solve a challenge"""
    return (
        CaptchaTypes.RE_CAPTCHA
        if payload['name="cf_captcha_kind" value'] == "re"
        else CaptchaTypes.H_CAPTCHA
    )
