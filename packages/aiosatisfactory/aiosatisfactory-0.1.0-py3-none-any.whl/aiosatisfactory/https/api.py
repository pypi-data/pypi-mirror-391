import json, aiohttp
import ssl
from .models import (
    BaseResponse,
    HealthCheckResponse,
    PasswordlessLoginResponse,
    PasswordLoginResponse,
    QueryServerStateResponse,
    GetServerOptionsResponse,
    GetAdvancedGameSettingsResponse,
    ClaimServerResponse,
    RunCommandResponse,
    ServerNewGameData,
    EnumerateSessionsResponse,
    DownloadSaveGameResponse,
    ErrorResponse
)

class ApiEndpoints():
    def __init__(self, session: aiohttp.ClientSession, url: str, headers: dict[str, str], ssl_context: ssl.SSLContext):
        self._session = session
        self._url = url
        self._headers = headers
        self._ssl_context = ssl_context

    async def _post(self, function: str, data: dict[str, str] = {}) -> aiohttp.ClientResponse:

        return await self._session.post(
            self._url,
            json={"function": function, "data": data},
            headers=self._headers,
            ssl=self._ssl_context
        )

    def _raise_error(self, response: aiohttp.ClientResponse, data: dict[str, str]) -> None:
        if response.status >= 400:
            raise ErrorResponse(data["errorCode"], data.get("errorMessage"), data.get("errorData"))


    async def health_check(self, client_custom_data: str = "") -> HealthCheckResponse:
        response = await self._post(
            "HealthCheck",
            {
                "ClientCustomData": client_custom_data
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        data = data["data"]
        return HealthCheckResponse(
            response.status,
            data["health"],
            data["serverCustomData"]
        )



    async def verify_authentication_token(self) -> BaseResponse:
        response = await self._post("VerifyAuthenticationToken")
        if response.status >= 400:
            data = await response.json()
            self._raise_error(response, data)
        return BaseResponse(response.status)


    async def passwordless_login(self, minimum_privilege_level: str) -> PasswordlessLoginResponse:
        response = await self._post(
            "PasswordlessLogin",
            {
                "MinimumPrivilegeLevel": minimum_privilege_level
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        data = data["data"]
        return PasswordlessLoginResponse(
            response.status,
            data["authenticationToken"]
        )



    async def passwordlogin(self, minimum_privilege_level: str, password: str) -> PasswordLoginResponse:
        response = await self._post(
            "PasswordLogin",
            {
                "MinimumPrivilegeLevel": minimum_privilege_level,
                "Password": password
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        data = data["data"]
        return PasswordLoginResponse(
            response.status,
            data["authenticationToken"]
        )



    async def query_server_state(self) -> QueryServerStateResponse:
        response = await self._post("QueryServerState")
        data = await response.json()
        self._raise_error(response, data)
        data = data["ServerGameState"]
        return QueryServerStateResponse(
            response.status,
            data["ActiveSessionName"],
            data["NumConnectedPlayers"],
            data["PlayerLimit"],
            data["TechTier"],
            data["ActiveSchematic"],
            data["GamePhase"],
            data["IsGameRunning"],
            data["TotalGameDuration"],
            data["IsGamePaused"],
            data["AverageTickRate"],
            data["AutoLoadSessionName"]
        )



    async def get_server_options(self) -> GetServerOptionsResponse:
        response = await self._post("GetServerOptions")
        data = await response.json()
        self._raise_error(response, data)
        return GetServerOptionsResponse(
            response.status,
            data["ServerOptions"],
            data["PendingServerOptions"]
        )



    async def get_advanced_game_settings(self) -> GetAdvancedGameSettingsResponse:
        response = await self._post("GetAdvancedGameSettings")
        data = await response.json()
        self._raise_error(response, data)
        return GetAdvancedGameSettingsResponse(
            response.status,
            data["CreativeModeEnabled"],
            data["AdvancedGameSettings"]
            )



    async def apply_advanced_game_settings(self, applied_advanced_game_settings: dict[str, str]) -> BaseResponse:
        response = await self._post(
            "ApplyAdvancedGameSettings",
            {
                "AppliedAdvancedGameSettings": json.dumps(applied_advanced_game_settings)
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def claim_server(self, server_name: str, admin_password: str) -> ClaimServerResponse:
        response = await self._post(
            "ClaimServer",
            {
                "ServerName": server_name,
                "AdminPassword": admin_password
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return ClaimServerResponse(
            response.status,
            data["authenticationToken"]
        )



    async def rename_server(self, server_name: str) -> BaseResponse:
        response = await self._post(
            "RenameServer",
            {
                "ServerName": server_name
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def set_client_password(self, password: str) -> BaseResponse:
        response = await self._post(
            "SetClientPassword",
            {
                "Password": password
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def set_admin_password(self, password: str, authentication_token: str) -> BaseResponse:
        response = await self._post(
            "SetAdminPassword",
            {
                "Password": password,
                "AuthenticationToken": authentication_token #??? - We have to generate a new token? - Maybe the documentation is wrong and this field is returned from the server?
            }
        ) 
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def set_auto_load_session_name(self, session_name: str) -> BaseResponse:
        response = await self._post(
            "SetAutoLoadSessionName",
            {
                "SessionName": session_name
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def run_command(self, command: str) -> RunCommandResponse:
        response = await self._post(
            "RunCommand",
            {
                "Command": command
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return RunCommandResponse(
            response.status,
            data["CommandResult"],
            data["ReturnValue"]
        )



    async def shutdown(self) -> BaseResponse:
        response = await self._post("Shutdown")
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def apply_server_options(self, updated_server_options: dict[str, str]) -> BaseResponse:
        response = await self._post(
            "ApplyServerOptions",
            {
                "UpdatedServerOptions": json.dumps(updated_server_options)
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def create_new_game(self, new_game_data: ServerNewGameData) -> BaseResponse:
        response = await self._post(
            "CreateNewGame",
            {
                "NewGameData": json.dumps(new_game_data)
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def save_game(self, save_name: str) -> BaseResponse:
        response = await self._post(
            "SaveGame",
            {
                "SaveName": save_name
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def delete_save_file(self, save_name: str) -> BaseResponse:
        response = await self._post(
            "DeleteSaveFile",
            {
                "SaveName": save_name
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def delete_save_session(self, session_name: str) -> BaseResponse:
        response = await self._post(
            "DeleteSaveSession",
            {
                "SessionName": session_name
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    async def enumerate_sessions(self) -> EnumerateSessionsResponse:
        response = await self._post("EnumerateSessions")
        data = await response.json()
        self._raise_error(response, data)
        return EnumerateSessionsResponse(
            response.status,
            data["Sessions"],
            data["CurrentSessionIndex"]
        )



    async def load_game(self, save_name: str, enable_advanced_game_settings: bool) -> BaseResponse:
        response = await self._post(
            "LoadGame",
            {
                "SaveName": save_name,
                "EnableAdvancedGameSettings": str(enable_advanced_game_settings)
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    #TODO
    async def upload_save_game(self, save_name: str, load_save_game: bool, enable_advanced_game_settings: bool) -> BaseResponse:
        response = await self._post(
            "UploadSaveGame",
            {
                "SaveName": save_name,
                "LoadSaveGame": str(load_save_game),
                "EnableAdvancedGameSettings": str(enable_advanced_game_settings)
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return BaseResponse(response.status)



    #TODO
    async def download_save_game(self, save_name: str) -> DownloadSaveGameResponse:
        response = await self._post(
            "DownloadSaveGame",
            {
                "SaveName": save_name
            }
        )
        data = await response.json()
        self._raise_error(response, data)
        return DownloadSaveGameResponse(
            response.status,
            data["SaveData"]
        )
