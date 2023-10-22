from enum import StrEnum, auto


class ChallengeStatus(StrEnum):
    PASSED = auto()  # dummy value representing a successful attempt
    H_CAPTCHA_V1 = auto()
    H_CAPTCHA_V2 = auto()
    IUAM_V1 = auto()
    IUAM_V2 = auto()
    FIREWALL_BLOCKED = auto()

    UNKNOWN = auto()


class CaptchaTypes(StrEnum):
    RE_CAPTCHA = auto()
    H_CAPTCHA = auto()
