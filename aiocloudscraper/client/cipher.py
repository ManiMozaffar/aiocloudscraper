from aiocloudscraper.types import Browser

MAP_BROWSER_TO_CIPHER: dict[Browser, list[str]] = {
    Browser.CHROME: [
        "TLS_AES_128_GCM_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-RSA-AES128-SHA",
        "ECDHE-RSA-AES256-SHA",
        "AES128-GCM-SHA256",
        "AES256-GCM-SHA384",
        "AES128-SHA",
        "AES256-SHA",
        "DES-CBC3-SHA",
    ],
    Browser.FIREFOX: [
        "TLS_AES_128_GCM_SHA256",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-AES256-SHA",
        "ECDHE-ECDSA-AES128-SHA",
        "ECDHE-RSA-AES128-SHA",
        "ECDHE-RSA-AES256-SHA",
        "DHE-RSA-AES128-SHA",
        "DHE-RSA-AES256-SHA",
        "AES128-SHA",
        "AES256-SHA",
        "DES-CBC3-SHA",
    ],
}
