from abc import ABC, abstractmethod
from dataclasses import dataclass

from httpx import URL

from aiocloudscraper.types import CaptchaTypes


@dataclass
class Proxy:
    host: str
    port: int
    username: str
    password: str


class AbstractCaptchaSolver(ABC):
    def __init__(self, proxy: Proxy | None = None, user_agent: str | None = None):
        self.proxy = proxy
        self.user_agent = user_agent
        self.init_auth()

    @abstractmethod
    def init_auth(self):
        ...

    @abstractmethod
    async def get_captcha_answer(self, captcha_type: CaptchaTypes, url: URL):
        pass

    async def solve_captcha(self, captcha_type: CaptchaTypes, url: URL):
        return self.get_captcha_answer(captcha_type, url)
