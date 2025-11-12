import aiohttp
from .lightweight import LightweightAPI
from .https import HttpsAPI


class SatisfactoryServer:
    def __init__(self, host: str, port: int = 7777, self_signed_certificate: bool = True, session: aiohttp.ClientSession | None = None, api_token: str = ""):
        self._lightweight = LightweightAPI(host, port)
        if session is None:
            self._https = None
        else:
            self._https = HttpsAPI(self_signed_certificate, host, port, session, api_token)

    @property
    def lightweight(self) -> LightweightAPI:
        return self._lightweight
    
    @property
    def https(self) -> HttpsAPI | None:
        return self._https

