from random import randint
from ..network import Network, Socket
from ..crypto import Cryption
from ..utils import Utils
import asyncio


class Methods:

    def __init__(self, sessionData:dict, platform:str, apiVersion:int, proxy:str, timeOut:int, showProgressBar:bool) -> None:
        self.platform = platform.lower()
        if not self.platform in ["android", "web", "rubx", "rubikax", "rubino"]:
            print("The \"{}\" is not a valid platform. Choose these one -> (web, android, rubx)".format(platform))
            exit()
        self.apiVersion = apiVersion
        self.proxy = proxy
        self.timeOut = timeOut
        self.showProgressBar = showProgressBar
        self.sessionData = sessionData
        self.crypto = Cryption(
            auth=sessionData["auth"],
            private_key=sessionData["private_key"]
        ) if sessionData else Cryption(auth=Utils.randomTmpSession())
        # network and socket are created lazily to support async session injection
        self._network: Network | None = None
        self._socket: Socket | None = None

    async def get_network(self, session=None) -> Network:
        if self._network:
            return self._network
        self._network = Network(methods=self, session=session)
        return self._network

    def get_socket(self) -> Socket:
        if self._socket:
            return self._socket
        self._socket = Socket(methods=self)
        return self._socket


    async def sendCode(self, phoneNumber:str, passKey:str=None, sendInternal:bool=False, session=None) -> dict:
        input:dict = {
            "phone_number": f"98{Utils.phoneNumberParse(phoneNumber)}",
            "send_type": "Internal" if sendInternal else "SMS",
        }

        if passKey:
            input["pass_key"] = passKey

        network = await self.get_network(session=session)
        return await network.request(
            method="sendCode",
            input=input,
            tmpSession=True
        )
    
    async def signIn(self, phoneNumber, phoneCodeHash, phoneCode, session=None) -> dict:
        publicKey, privateKey = self.crypto.rsaKeyGenrate()

        network = await self.get_network(session=session)
        data = await network.request(
            method="signIn",
            input={
                "phone_number": f"98{Utils.phoneNumberParse(phoneNumber)}",
                "phone_code_hash": phoneCodeHash,
                "phone_code": phoneCode,
                "public_key": publicKey
            },
            tmpSession=True
        )

        data["private_key"] = privateKey

        return data
    
    async def registerDevice(self, deviceModel, session=None) -> dict:
        network = await self.get_network(session=session)
        return await network.request(
            method="registerDevice",
            input={
                "app_version": "WB_4.3.3" if self.platform == "web" else "MA_3.4.3",
                "device_hash": Utils.randomDeviceHash(),
                "device_model": deviceModel,
                "is_multi_account": False,
                "lang_code": "fa",
                "system_version": "Windows 11" if self.platform == "web" else "SDK 28",
                "token": "",
                "token_type": "Web" if self.platform == "web" else "Firebase"
            }
        )
    
    async def getChatAllMembers(self, objectGuid:str, searchText:str, startId:str, justGetGuids:bool=False, session=None) -> dict:
        chatType:str = Utils.getChatTypeByGuid(objectGuid=objectGuid)
        network = await self.get_network(session=session)
        data = await network.request(
            method=f"get{chatType}AllMembers",
            input={
                f"{chatType.lower()}_guid": objectGuid,
                "search_text": searchText.replace("@", "") if searchText else searchText,
                "start_id": startId
            }
        )

        if justGetGuids:
            return [i["member_guid"] for i in data["in_chat_members"]]

        return data