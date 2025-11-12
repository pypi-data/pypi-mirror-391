from json import dumps, loads
from tqdm import tqdm
import aiohttp
import aiofiles
import asyncio
from ..utils import Configs
from ..exceptions import *
from .helper import Helper


class Network:

    def __init__(self, methods: object, session: aiohttp.ClientSession = None) -> None:
        self.methods = methods
        self.sessionData = methods.sessionData
        self.crypto = methods.crypto
        self._external_session = session
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._external_session:
            return self._external_session
        if self._session and not self._session.closed:
            return self._session
        timeout = aiohttp.ClientTimeout(total=self.methods.timeOut)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        self._session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(self, method: str, input: dict = {}, tmpSession: bool = False, attempt: int = 0, maxAttempt: int = 2):
        url: str = await Helper.get_api_server()
        platform: str = self.methods.platform.lower()
        apiVersion: int = self.methods.apiVersion

        if platform in ["rubx", "rubikax"]:
            client: dict = Configs.clients["android"].copy()
            client["package"] = "ir.rubx.bapp"
        elif platform in ["android"]:
            client: dict = Configs.clients["android"].copy()
        else:
            client: dict = Configs.clients["web"].copy()

        payload = {
            "method": method,
            "input": input,
            "client": client
        }

        data = {
            "api_version": str(apiVersion),
            "data_enc": self.crypto.encrypt(dumps(payload))
        }

        if tmpSession:
            data["tmp_session"] = self.crypto.auth
        else:
            if apiVersion > 5:
                data["auth"] = self.crypto.changeAuthType(self.sessionData["auth"]) if self.sessionData and self.sessionData.get("auth") else self.sessionData.get("auth")
            else:
                data["auth"] = self.sessionData.get("auth")

        headers: dict = {
            "Referer": "https://web.rubika.ir/",
            "Content-Type": "application/json; charset=utf-8"
        }

        if not tmpSession and apiVersion > 5:
            data["sign"] = self.crypto.makeSignFromData(data["data_enc"])

        session = await self._get_session()

        last_exc = None
        for attempt in range(maxAttempt + 1):
            try:
                async with session.post(url, json=data, headers=headers) as resp:
                    resp.raise_for_status()
                    text = await resp.text()
                    try:
                        decrypted = loads(self.crypto.decrypt(loads(text)["data_enc"]))
                    except Exception:
                        raise

                    if decrypted["status"] == "OK":
                        if tmpSession:
                            decrypted["data"]["tmp_session"] = self.crypto.auth
                        return decrypted["data"]

                    raise {
                        "INVALID_AUTH": InvalidAuth(),
                        "NOT_REGISTERED": NotRegistered(),
                        "INVALID_INPUT": InvalidInput(),
                        "TOO_REQUESTS": TooRequests()
                    }[decrypted.get("status_det")]

            except Exception as e:
                last_exc = e
                await asyncio.sleep(0.1 * (attempt + 1))
                continue

        raise last_exc

    async def upload(self, file: str | bytes, fileName: str = None, chunkSize: int = 131072):
        from ..utils import Utils

        # normalize to bytes
        if isinstance(file, str):
            if Utils.checkLink(url=file):
                session = await self._get_session()
                async with session.get(file) as resp:
                    file_bytes = await resp.read()
                file = file_bytes
                mime: str = Utils.getMimeFromByte(bytes=file)
                fileName = fileName or Utils.generateFileName(mime=mime)
            else:
                fileName = fileName or file
                mime = file.split(".")[-1]
                async with aiofiles.open(file, "rb") as fh:
                    file = await fh.read()

        elif not isinstance(file, (bytes, bytearray)):
            raise FileNotFoundError("Enter a valid path or url or bytes of file.")
        else:
            mime = Utils.getMimeFromByte(bytes=file)
            fileName = fileName or Utils.generateFileName(mime=mime)

        requestSendFileData: dict = await asyncio.get_event_loop().run_in_executor(None, lambda: self.methods.requestSendFile(fileName=fileName, mime=mime, size=len(file)))

        header = {
            "auth": self.sessionData["auth"],
            "access-hash-send": requestSendFileData["access_hash_send"],
            "file-id": requestSendFileData["id"],
        }

        totalParts = (len(file) + chunkSize - 1) // chunkSize

        if self.methods.showProgressBar:
            processBar = tqdm(
                desc=f"Uploading {fileName}",
                total=len(file),
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            )

        session = await self._get_session()

        async def send_chunk(data: bytes, maxAttempts: int = 2):
            last_exc = None
            for _ in range(maxAttempts):
                try:
                    async with session.post(requestSendFileData["upload_url"], data=data, headers=header) as resp:
                        resp.raise_for_status()
                        text = await resp.text()
                        return loads(text)
                except Exception as e:
                    last_exc = e
                    await asyncio.sleep(0.1)
            raise last_exc

        for partNumber in range(1, totalParts + 1):
            startIdx = (partNumber - 1) * chunkSize
            endIdx = min(startIdx + chunkSize, len(file))
            header["chunk-size"] = str(endIdx - startIdx)
            header["part-number"] = str(partNumber)
            header["total-part"] = str(totalParts)
            data = file[startIdx:endIdx]

            hashFileReceive = await send_chunk(data)

            if self.methods.showProgressBar:
                processBar.update(len(data))

            if not hashFileReceive:
                return

            if partNumber == totalParts:
                if not hashFileReceive.get("data"):
                    return

                requestSendFileData["file"] = None
                requestSendFileData["access_hash_rec"] = hashFileReceive["data"]["access_hash_rec"]
                requestSendFileData["file_name"] = fileName
                requestSendFileData["mime"] = mime
                requestSendFileData["size"] = len(file)
                return requestSendFileData

    async def download(self, accessHashRec: str, fileId: str, dcId: str, size: int, fileName: str, chunkSize: int = 262143, attempt: int = 0, maxAttempts: int = 2):
        headers: dict = {
            "auth": self.sessionData["auth"],
            "access-hash-rec": accessHashRec,
            "dc-id": dcId,
            "file-id": fileId,
            "Host": f"messenger{dcId}.iranlms.ir",
            "client-app-name": "Main",
            "client-app-version": "3.5.7",
            "client-package": "app.rbmain.a",
            "client-platform": "Android",
            "Connection": "Keep-Alive",
            "Content-Type": "application/json",
            "User-Agent": "okhttp/3.12.1"
        }

        session = await self._get_session()
        url = f"https://messenger{dcId}.iranlms.ir/GetFile.ashx"

        async with session.post(url, headers=headers) as resp:
            resp.raise_for_status()
            data = bytearray()

            if self.methods.showProgressBar:
                processBar = tqdm(
                    desc=f"Downloading {fileName}",
                    total=size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                )

            async for chunk in resp.content.iter_chunked(chunkSize):
                data.extend(chunk)
                if self.methods.showProgressBar:
                    processBar.update(len(chunk))
                if len(data) >= size:
                    return bytes(data)

        raise TimeoutError("Failed to download the file!")
            
    def download(self, accessHashRec:str, fileId:str, dcId:str, size:int, fileName:str, chunkSize:int=262143, attempt:int=0, maxAttempts:int=2):
        headers:dict = {
            "auth": self.sessionData["auth"],
            "access-hash-rec": accessHashRec,
            "dc-id": dcId,
            "file-id": fileId,
            "Host": f"messenger{dcId}.iranlms.ir",
            "client-app-name": "Main",
            "client-app-version": "3.5.7",
            "client-package": "app.rbmain.a",
            "client-platform": "Android",
            "Connection": "Keep-Alive",
            "Content-Type": "application/json",
            "User-Agent": "okhttp/3.12.1"
        }


        response = self.http.request(
            "POST",
            url=f"https://messenger{dcId}.iranlms.ir/GetFile.ashx",
            headers=headers,
            preload_content=False
        )

        data:bytes = b""

        if self.methods.showProgressBar:
            processBar = tqdm(
                desc=f"Downloading {fileName}",
                total=size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            )

        for downloadedData in response.stream(chunkSize):
            try:
                if downloadedData:
                    data += downloadedData
                    if self.methods.showProgressBar:
                        processBar.update(len(downloadedData))

                if len(data) >= size:
                    return data
            except Exception:
                if attempt <= maxAttempts:
                    attempt += 1
                    print(f"\nError downloading file! (Attempt {attempt}/{maxAttempts})")
                    continue

                raise TimeoutError("Failed to download the file!")