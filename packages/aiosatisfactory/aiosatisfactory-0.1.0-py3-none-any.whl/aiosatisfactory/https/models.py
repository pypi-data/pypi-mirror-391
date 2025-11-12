from dataclasses import dataclass



@dataclass(slots=True)
class BaseResponse:
    status_code: int



@dataclass(slots=True)
class HealthCheckResponse(BaseResponse):
    health: str
    server_custom_data: str



@dataclass(slots=True)
class PasswordlessLoginResponse(BaseResponse):
    authentication_token: str



@dataclass(slots=True)
class PasswordLoginResponse(BaseResponse):
    authentication_token: str



@dataclass(slots=True)
class QueryServerStateResponse(BaseResponse):
    active_session_name: str
    num_connected_players: int
    player_limit: int
    tech_tier: int
    active_schematic: str
    game_phase: str
    is_game_running: bool
    total_game_duration: int
    is_game_paused: bool
    average_tick_rate: float
    auto_load_session_name: str



@dataclass(slots=True)
class GetServerOptionsResponse(BaseResponse):
    server_options: dict[str, str]
    pending_server_options: dict[str, str]



@dataclass(slots=True)
class GetAdvancedGameSettingsResponse(BaseResponse):
    creative_mode_enabled: bool
    advanced_game_settings: dict[str, str]



@dataclass(slots=True)
class ClaimServerResponse(BaseResponse):
    authentication_token: str



@dataclass(slots=True)
class RunCommandResponse(BaseResponse):
    command_result: str
    return_value: bool



@dataclass(slots=True)
class ServerNewGameData:
    session_name: str
    map_name: str
    starting_location: str
    skip_onboarding: bool
    advanced_game_settings: dict[str, str]
    custom_options_only_for_modding: dict[str, str]



@dataclass(slots=True)
class SaveHeader:
    save_version: int
    build_version: int
    save_name: str
    map_name: str
    map_options: str
    session_name: str
    play_duration_seconds: int
    save_date_time: str
    is_modded_save: bool
    is_edited_save: bool
    is_creative_mode_enabled: bool

@dataclass(slots=True)
class SessionSaveStruct:
    session_name: str
    save_headers: list[SaveHeader]

@dataclass(slots=True)
class EnumerateSessionsResponse(BaseResponse):
    sessions: list[SessionSaveStruct]
    current_session_index: int

@dataclass(slots=True)
class DownloadSaveGameResponse(BaseResponse):
    save_data: bytes



@dataclass(slots=True)
class ErrorResponse(Exception):
    error_code: str
    error_message: str | None = None
    error_details: str | None = None