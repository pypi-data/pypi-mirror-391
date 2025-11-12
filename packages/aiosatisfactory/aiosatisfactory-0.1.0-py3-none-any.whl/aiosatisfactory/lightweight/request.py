import struct

from .const import (
    PROTOCOL_MAGIC_FORMAT, PROTOCOL_MAGIC_OFFSET,
    MESSAGE_TYPE_FORMAT, MESSAGE_TYPE_OFFSET,
    PROTOCOL_VERSION_FORMAT, PROTOCOL_VERSION_OFFSET,
    COOKIE_FORMAT, COOKIE_OFFSET,
    TERMINATOR_BYTE_FORMAT, TERMINATOR_BYTE_OFFSET,
)

class ServerStateRequest:
    def __init__(self, raw_request: bytes):
        self.raw_request = raw_request

    @property
    def ProtocolMagic(self) -> str:
        return struct.unpack_from(PROTOCOL_MAGIC_FORMAT, self.raw_request, PROTOCOL_MAGIC_OFFSET)[0]
    
    @property
    def MessageType(self) -> int:
        return struct.unpack_from(MESSAGE_TYPE_FORMAT, self.raw_request, MESSAGE_TYPE_OFFSET)[0]

    @property
    def ProtocolVersion(self) -> int:
        return struct.unpack_from(PROTOCOL_VERSION_FORMAT, self.raw_request, PROTOCOL_VERSION_OFFSET)[0]

    @property
    def Cookie(self) -> int:
        return struct.unpack_from(COOKIE_FORMAT, self.raw_request, COOKIE_OFFSET)[0]
    
    @property
    def TerminatorByte(self) -> int:
        return struct.unpack_from(TERMINATOR_BYTE_FORMAT, self.raw_request, TERMINATOR_BYTE_OFFSET)[0]