from ..methods import Methods
import asyncio


class Client(object):

    def __init__(
        self,
        session:str=None,
        auth:str=None,
        private:str=None,
        platform:str="web",
        api_version:int=6,
        proxy:str=None,
        time_out:int=10,
        show_progress_bar:bool=True
    ) -> None:
        
        self.session = session
        self.platform = platform
        self.apiVersion = api_version
        self.proxy = proxy
        self.timeOut = time_out
        
        if(session):
            from ..sessions import Sessions
            self.sessions = Sessions(self)

            if(self.sessions.cheackSessionExists()):
                self.sessionData = self.sessions.loadSessionData()
            else:
                self.sessionData = self.sessions.createSession()
        else:
            from ..utils import Utils
            self.sessionData = {
                "auth": auth,
                "private_key": Utils.privateParse(private=private)
            }

        self.methods = Methods(
            sessionData=self.sessionData,
            platform=platform,
            apiVersion=api_version,
            proxy=proxy,
            timeOut=time_out,
            showProgressBar=show_progress_bar
        )

    async def _ensure_network(self, session=None):
        # Ensure an async Network is initialized
        await self.methods.get_network(session=session)

    async def send_code(self, phone_number:str, pass_key:str=None, session=None) -> dict:
        return await self.methods.sendCode(phoneNumber=phone_number, passKey=pass_key, session=session)
    
    async def sign_in(self, phone_number:str, phone_code_hash:str, phone_code:str, session=None) -> dict:
        return await self.methods.signIn(phoneNumber=phone_number, phoneCodeHash=phone_code_hash, phoneCode=phone_code, session=session)
    
    async def register_device(self, device_model:str, session=None) -> dict:
        return await self.methods.registerDevice(deviceModel=device_model, session=session)
    
    async def logout(self) -> dict:
        # placeholder - implement async logout if needed
        if hasattr(self.methods, 'logout'):
            maybe = self.methods.logout
            if asyncio.iscoroutinefunction(maybe):
                return await maybe()
            # keep sync logout if defined
            return await asyncio.get_event_loop().run_in_executor(None, maybe)
        return {}
    
    async def get_all_members(self, object_guid:str, search_text:str=None, start_id:str=None, just_get_guids:bool=False, session=None) -> dict:
        return await self.methods.getChatAllMembers(objectGuid=object_guid, searchText=search_text, startId=start_id, justGetGuids=just_get_guids, session=session)

    # NOTE: sync wrappers removed to keep the client fully async. Use
    # `asyncio.run(client.send_code(...))` from application level if you need
    # to call from synchronous code.