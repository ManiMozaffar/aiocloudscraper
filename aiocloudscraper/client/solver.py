from httpx import URL

from aiocloudscraper.solvers.base import AbstractCaptchaSolver


class HCaptchaSolver:
    async def solve_captcha(self, solver: AbstractCaptchaSolver, body: str, url: URL):
        """Solves captcha using third party

        Args:
            solver (AbstractCaptchaSolver): _description_
            body (str): _description_
            url (URL): _description_
        """
        # TODO: finish this at last
        ...


class ReCaptchaSolver:
    async def solve_captcha(self, solver: AbstractCaptchaSolver, body: str, url: URL):
        """Solves captcha using third party

        Args:
            solver (AbstractCaptchaSolver): _description_
            body (str): _description_
            url (URL): _description_
        """
        # TODO: finish this at last
        ...
