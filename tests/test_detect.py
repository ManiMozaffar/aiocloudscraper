import pytest

from aiocloudscraper.client.http import Browser, Client

url = "https://www.whatsmydns.net/#NS/"
# url = "https://www.nowsecure.nl/"


@pytest.mark.asyncio
async def test_detect():
    async with Client(
        browser=Browser.FIREFOX, ecdh_curve="secp384r1", verify=False
    ) as client:
        resp = await client.get(url)
        print(resp.status_code)
