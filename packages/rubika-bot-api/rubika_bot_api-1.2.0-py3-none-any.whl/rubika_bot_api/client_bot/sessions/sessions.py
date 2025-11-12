from os.path import exists
from json import loads, dumps
import aiofiles
import asyncio


class Sessions:

    def __init__(self, client:object) -> None:
        self.client = client
    def _session_path(self) -> str:
        return f"{self.client.session}.mojia"

    async def cheackSessionExists(self) -> bool:
        """Async check whether the session file exists."""
        return await asyncio.to_thread(exists, self._session_path())

    async def loadSessionData_async(self) -> dict:
        """Async load session JSON using aiofiles."""
        async with aiofiles.open(self._session_path(), encoding="UTF-8") as f:
            text = await f.read()
            return loads(text)

    # Keep a synchronous compatibility method but prefer the async version
    def loadSessionData(self):
        """Synchronous fallback (kept for compatibility). Prefer `loadSessionData_async`."""
        with open(self._session_path(), encoding="UTF-8") as f:
            return loads(f.read())

    async def saveSessionData_async(self, sessionData: dict):
        """Async save session JSON using aiofiles."""
        async with aiofiles.open(self._session_path(), "w", encoding="UTF-8") as f:
            await f.write(dumps(sessionData, indent=4))

    def _createSession_blocking(self):
        """Blocking implementation of the interactive session creation.
        This function is run in a thread pool by the async wrapper so the
        event loop isn't blocked.
        """
        # Keep existing interactive CLI flow synchronous for compatibility
        from ..methods import Methods
        methods:object = Methods(
            sessionData={},
            platform=self.client.platform,
            apiVersion=6,
            proxy=self.client.proxy,
            timeOut=self.client.timeOut,
            showProgressBar=True
        )

        while True:
            phoneNumber:str = input("\nphone number :\t")
            try:
                sendCodeData:dict = methods.sendCode(phoneNumber=phoneNumber)
            except Exception:
                print("The phone number is invalid! Please try again.")
                continue

            if sendCodeData.get('status') == 'SendPassKey':
                while True:
                    passKey:str = input(f'\npass key [{sendCodeData.get("hint_pass_key")}]  : ')
                    sendCodeData:dict = methods.sendCode(phoneNumber=phoneNumber, passKey=passKey)
                    
                    if sendCodeData.get('status') == 'InvalidPassKey':
                        print(f'\nThe pass key({sendCodeData.get("hint_pass_key")}) try again.')
                        continue
                    break
            
            while True:
                phoneCode:str = input("\ncode : ").strip()
                signInData:dict = methods.signIn(phoneNumber=phoneNumber, phoneCodeHash=sendCodeData['phone_code_hash'], phoneCode=phoneCode)
                if signInData.get('status') != 'OK':
                    print("The code is invalid! Please try again.")
                    continue
                break
            
            from ..crypto import Cryption

            sessionData = {
                'auth': Cryption.decryptRsaOaep(signInData["private_key"], signInData['auth']),
                'private_key': signInData["private_key"],
                'user': signInData['user'],
            }

            with open(self._session_path(), "w", encoding="UTF-8") as f:
                f.write(dumps(sessionData, indent=4))

            Methods(
                sessionData=sessionData,
                platform=self.client.platform,
                apiVersion=6,
                proxy=self.client.proxy,
                timeOut=self.client.timeOut,
                showProgressBar=True
            ).registerDevice(deviceModel=f"mojia-BotClient-{self.client.session}")
            print(f"\nSign successful")

            return sessionData

    async def createSession(self):
        """Async wrapper that runs the interactive blocking flow in an executor.

        This keeps the public API async while preserving the original
        interactive behaviour (input(), blocking network calls) by moving the
        blocking work into a thread.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._createSession_blocking)