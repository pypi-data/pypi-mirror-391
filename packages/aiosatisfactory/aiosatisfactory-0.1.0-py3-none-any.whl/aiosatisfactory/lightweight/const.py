"""Constants for Satisfactory LightWeight Query protocol."""

"""
All the data in this protocol is in little-endian byte order as stated in the official documentation
The conversion between the documentation DataType and struct formats is as follows:
- uint8  -> B
- uint16 -> H
- uint32 -> L
- uint64 -> Q
- uint8[] -> s
"""

"""General purpose fields and formats."""

PROTOCOL_MAGIC: int = 0xF6D5
PROTOCOL_MAGIC_FORMAT: str = "<H"
PROTOCOL_MAGIC_OFFSET: int = 0

MESSAGE_TYPE_FORMAT: str = "<B"
MESSAGE_TYPE_OFFSET: int = 2

PROTOCOL_VERSION: int = 1
PROTOCOL_VERSION_FORMAT: str = "<B"
PROTOCOL_VERSION_OFFSET: int = 3

# The payload starts after the 3-byte header, we use this constant to have a direct reference to the documentation offsets
PAYLOAD_START_BYTE: int = 4

# The payload always starts with a cookie to identify the request/response pair
COOKIE_FORMAT: str = "<Q"
COOKIE_OFFSET: int = PAYLOAD_START_BYTE + 0

# The last byte is always the terminator byte
TERMINATOR_BYTE: int = 0x01
TERMINATOR_BYTE_FORMAT: str = "<B"
TERMINATOR_BYTE_OFFSET: int = -1

"""Poll specific field formats and offsets."""

MESSAGE_TYPE_POLL: int = 0

POLL_FORMAT: str = "<HBBQB"

SUB_STATES_STRUCTURE_SIZE: int = 3

"""Response specific field formats and offsets."""

MESSAGE_TYPE_RESPONSE: int = 1

SERVER_STATE_FORMAT: str = "<B"
SERVER_STATE_OFFSET: int = PAYLOAD_START_BYTE + 8

SERVER_NET_CL_FORMAT: str = "<L"
SERVER_NET_CL_OFFSET: int = PAYLOAD_START_BYTE + 9

SERVER_FLAGS_FORMAT: str = "<Q"
SERVER_FLAGS_OFFSET: int = PAYLOAD_START_BYTE + 13

NUM_SUB_STATES_FORMAT: str = "<B"
NUM_SUB_STATES_OFFSET: int = PAYLOAD_START_BYTE + 21

# The sub-states section directly start with the first sub state ID
SUB_STATE_ID_FORMAT: str = "<B"
SUB_STATE_ID_OFFSET: int = PAYLOAD_START_BYTE + 22

# The sub-state version follows after it's ID, the documentation has a typo here saying there is an 8 bytes offset
SUB_STATE_VERSION_FORMAT: str = "<H"
BASE_SUB_STATE_VERSION_OFFSET: int = PAYLOAD_START_BYTE + 22 + 1

SERVER_NAME_LENGTH_FORMAT: str = "<H"
BASE_SERVER_NAME_LENGTH_OFFSET: int = PAYLOAD_START_BYTE + 22

# {} is to be replaced with the length of the server name + 1
SERVER_NAME_FORMAT: str = "<{}s"
BASE_SERVER_NAME_OFFSET: int = PAYLOAD_START_BYTE + 22 + 1
