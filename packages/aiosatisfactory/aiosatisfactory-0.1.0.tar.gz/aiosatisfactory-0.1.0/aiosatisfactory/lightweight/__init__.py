import struct
from .udp import udp_query
from .response import ServerStateResponse
from .request import ServerStateRequest

from .const import (
    POLL_FORMAT,
    PROTOCOL_MAGIC,
    MESSAGE_TYPE_POLL,
    PROTOCOL_VERSION,
    TERMINATOR_BYTE
)

class LightweightAPIResult():
    def __init__(self, request: ServerStateRequest, response: ServerStateResponse):
        self._request = request
        self._response = response

    @property
    def request(self) -> ServerStateRequest:
        return self._request

    @property
    def response(self) -> ServerStateResponse:
        return self._response

class LightweightAPI():
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    async def query(self, Cookie: int) -> LightweightAPIResult | None:

        request = struct.pack(POLL_FORMAT, PROTOCOL_MAGIC, MESSAGE_TYPE_POLL, PROTOCOL_VERSION, Cookie, TERMINATOR_BYTE)
        response = await udp_query(self._host, self._port, request)
        if response is None:
            return None
        return LightweightAPIResult(ServerStateRequest(request), ServerStateResponse(response))
