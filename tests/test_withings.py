import pytest

from aiocloudscraper.client.http import Browser, Client

url = (
    "https://support.withings.com/hc/en-us/sections/360004896738"
    "?subsection_id=360004896738&section_id=6216126485393&"
    "&from_psection_name=Withings%20Developers%20Updates"
)
# url = "https://google.com"


@pytest.mark.asyncio
async def test_detect():
    async with Client(
        browser=Browser.CHROME, ecdh_curve="secp384r1", verify=False
    ) as client:
        resp = await client.get(url)
        print(resp.status_code)
