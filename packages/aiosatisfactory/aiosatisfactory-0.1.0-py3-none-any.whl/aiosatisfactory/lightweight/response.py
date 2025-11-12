import struct

from .const import (
    PROTOCOL_MAGIC_FORMAT, PROTOCOL_MAGIC_OFFSET,
    MESSAGE_TYPE_FORMAT, MESSAGE_TYPE_OFFSET,
    PROTOCOL_VERSION_FORMAT, PROTOCOL_VERSION_OFFSET,
    COOKIE_FORMAT, COOKIE_OFFSET,
    SERVER_STATE_FORMAT, SERVER_STATE_OFFSET,
    SERVER_NET_CL_FORMAT, SERVER_NET_CL_OFFSET,
    SERVER_FLAGS_FORMAT, SERVER_FLAGS_OFFSET,
    NUM_SUB_STATES_FORMAT, NUM_SUB_STATES_OFFSET,
    SUB_STATE_ID_FORMAT, SUB_STATE_ID_OFFSET,
    SUB_STATE_VERSION_FORMAT, BASE_SUB_STATE_VERSION_OFFSET,
    SERVER_NAME_LENGTH_FORMAT, BASE_SERVER_NAME_LENGTH_OFFSET,
    SERVER_NAME_FORMAT, BASE_SERVER_NAME_OFFSET,
    TERMINATOR_BYTE_FORMAT, TERMINATOR_BYTE_OFFSET,
    SUB_STATES_STRUCTURE_SIZE
)

class ServerStateResponse:

    def __init__(self, raw_response: bytes):
        self.raw_response = raw_response

    @property
    def ProtocolMagic(self) -> str:
        return struct.unpack_from(PROTOCOL_MAGIC_FORMAT, self.raw_response, PROTOCOL_MAGIC_OFFSET)[0]
    
    @property
    def MessageType(self) -> int:
        return struct.unpack_from(MESSAGE_TYPE_FORMAT, self.raw_response, MESSAGE_TYPE_OFFSET)[0]

    @property
    def ProtocolVersion(self) -> int:
        return struct.unpack_from(PROTOCOL_VERSION_FORMAT, self.raw_response, PROTOCOL_VERSION_OFFSET)[0]

    @property
    def Cookie(self) -> int:
        return struct.unpack_from(COOKIE_FORMAT, self.raw_response, COOKIE_OFFSET)[0]

    @property
    def ServerState(self) -> int:
        return struct.unpack_from(SERVER_STATE_FORMAT, self.raw_response, SERVER_STATE_OFFSET)[0]

    @property
    def ServerNetCL(self) -> int:
        return struct.unpack_from(SERVER_NET_CL_FORMAT, self.raw_response, SERVER_NET_CL_OFFSET)[0]

    @property
    def ServerFlags(self) -> int:
        return struct.unpack_from(SERVER_FLAGS_FORMAT, self.raw_response, SERVER_FLAGS_OFFSET)[0]

    @property
    def NumSubStates(self) -> int:
        return struct.unpack_from(NUM_SUB_STATES_FORMAT, self.raw_response, NUM_SUB_STATES_OFFSET)[0]

    @property
    def SubStates(self) -> list[tuple[int, int]]:
        sub_states: list[tuple[int, int]] = []
        for i in range(self.NumSubStates):
            sub_state = (
                struct.unpack_from(SUB_STATE_ID_FORMAT, self.raw_response, SUB_STATE_ID_OFFSET + i * SUB_STATES_STRUCTURE_SIZE)[0],
                struct.unpack_from(SUB_STATE_VERSION_FORMAT, self.raw_response, BASE_SUB_STATE_VERSION_OFFSET + i * SUB_STATES_STRUCTURE_SIZE)[0]
            )
            sub_states.append(sub_state)
        return sub_states

    @property
    def ServerNameLength(self) -> int:
        return struct.unpack_from(SERVER_NAME_LENGTH_FORMAT, self.raw_response, BASE_SERVER_NAME_LENGTH_OFFSET + self.NumSubStates * SUB_STATES_STRUCTURE_SIZE)[0]

    @property
    def ServerName(self) -> str:
        calculated_server_name_format = SERVER_NAME_FORMAT.format(self.ServerNameLength + 1)
        calculated_server_name_offset = BASE_SERVER_NAME_OFFSET + self.NumSubStates * SUB_STATES_STRUCTURE_SIZE
        return struct.unpack_from(calculated_server_name_format, self.raw_response, calculated_server_name_offset)[0].decode('utf-8')

    @property
    def TerminatorByte(self) -> int:
        return struct.unpack_from(TERMINATOR_BYTE_FORMAT, self.raw_response, TERMINATOR_BYTE_OFFSET)[0]
