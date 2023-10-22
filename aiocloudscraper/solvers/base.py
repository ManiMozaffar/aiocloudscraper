from abc import ABC, abstractmethod

from httpx import URL


class AbstractCaptchaSolver(ABC):
    def __init__(self):
        ...

    @abstractmethod
    def get_captcha_answer(self, captcha_type: str, url: URL, site_key: str, captcha_params: dict):
        pass

    def solve_captcha(self, captcha_type: str, url: URL, site_key: str, captcha_params: dict):
        return self.get_captcha_answer(captcha_type, url, site_key, captcha_params)
