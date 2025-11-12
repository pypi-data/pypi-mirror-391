# Filters
import asyncio
import logging
import mimetypes
import re
from typing import Any, Dict, List, Optional, Union

from rubika_bot_api.bot.models import Update, InlineMessage

logger = logging.getLogger(__name__)


def maybe_instance(f):
    return f() if isinstance(f, type) else f


class FilterMeta(type):
    def __and__(cls, other):
        return AndFilter(maybe_instance(cls), maybe_instance(other))

    def __rand__(cls, other):
        return AndFilter(maybe_instance(other), maybe_instance(cls))

    def __or__(cls, other):
        return OrFilter(maybe_instance(cls), maybe_instance(other))

    def __ror__(cls, other):
        return OrFilter(maybe_instance(other), maybe_instance(cls))

    def __invert__(cls):
        return NotFilter(maybe_instance(cls))


class Filter(metaclass=FilterMeta):
    async def check(self, update):
        raise NotImplementedError

    def __and__(self, other):
        return AndFilter(maybe_instance(self), maybe_instance(other))

    def __rand__(self, other):
        return AndFilter(maybe_instance(other), maybe_instance(self))

    def __or__(self, other):
        return OrFilter(maybe_instance(self), maybe_instance(other))

    def __ror__(self, other):
        return OrFilter(maybe_instance(other), maybe_instance(self))

    def __invert__(self):
        instance = self() if isinstance(self, type) else self
        return NotFilter(instance)


class AndFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    async def check(self, update: Union["Update", "InlineMessage"]) -> bool:
        for f in self.filters:
            if isinstance(f, type):  # اگر کلاس دادیم
                f = f()
            if not await f.check(update):
                return False
        return True


class OrFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    async def check(self, update):
        for f in self.filters:
            if isinstance(f, type):
                f = f()
            if await f.check(update):
                return True
        return False


class NotFilter(Filter):
    def __init__(self, f: Filter):
        self.f = f if not isinstance(f, type) else f()

    async def check(self, update):
        return not await self.f.check(update)


class text(Filter):
    def __init__(self, text: Optional[str] = None, regex: bool = False):
        self.text = text
        self.regex = regex
        self._compiled = re.compile(text) if regex and text else None

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            text = update.find_key("text")
        except KeyError:
            return False
            
        if not text:
            return False

        if not self.text:
            return True

        if self.regex:
            return bool(self._compiled.match(text))

        return text == self.text


class commands(Filter):
    def __init__(
        self,
        commands: Union[str, List[str]],
        prefixes: List[str] = ["/"],
        case_sensitive: bool = False,
        allow_no_prefix: bool = False,
    ):
        self.commands = [commands] if isinstance(commands, str) else commands
        self.prefixes = prefixes
        self.case_sensitive = case_sensitive
        self.allow_no_prefix = allow_no_prefix

        if not case_sensitive:
            self.commands = [cmd.lower() for cmd in self.commands]

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        text = (
            update.new_message.text
            if isinstance(update, Update) and update.new_message
            else update.text if isinstance(update, InlineMessage) else ""
        )
        if not text:
            return False

        check_text = text if self.case_sensitive else text.lower()

        parts = check_text.split(maxsplit=1)
        command_part = parts[0]

        for cmd in self.commands:
            for prefix in self.prefixes:
                if command_part == f"{prefix}{cmd}" or command_part.startswith(
                    f"{prefix}{cmd}"
                ):
                    return True

            if self.allow_no_prefix and (
                command_part == cmd or command_part.startswith(cmd)
            ):
                return True

        return False


class update_type(Filter):
    def __init__(self, update_types: Union[str, List[str]]):
        self.update_types = (
            [update_types] if isinstance(update_types, str) else update_types
        )

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        result = (isinstance(update, Update) and update.type in self.update_types) or (
            isinstance(update, InlineMessage) and "InlineMessage" in self.update_types
        )
        logger.debug(f"UpdateTypeFilter check: types={self.update_types}, update.type={update.type if isinstance(update, Update) else 'InlineMessage'}, result={result}")
        return result


class private(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return bool(update.chat_id.startswith("b0"))


class group(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return bool(update.chat_id.startswith("g0"))


class channel(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return bool(update.chat_id.startswith("c0"))


class bot(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        sender_type = (
            update.new_message.sender_type
            if isinstance(update, Update) and update.new_message
            else update.updated_message.sender_type if update.updated_message else ""
        )
        if not sender_type:
            return False
        return sender_type == "Bot"


class chat(Filter):
    def __init__(self, chat_id: Union[List[str], str]):
        self.chats = [chat_id] if isinstance(chat_id, str) else chat_id

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return update.chat_id in self.chats


class button(Filter):
    def __init__(self, button_id: str, regex: bool = False):
        self.regex = regex
        self.button_id = re.compile(button_id) if regex else button_id

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        aux_data = None

        if isinstance(update, Update):
            message = update.new_message or update.updated_message
            if message:
                aux_data = message.aux_data
        elif isinstance(update, InlineMessage):
            aux_data = update.aux_data

        if not aux_data:
            return False

        button_id = aux_data.get("button_id") or aux_data.get("callback_data")
        if not button_id:
            for value in aux_data.values():
                if isinstance(value, dict):
                    button_id = value.get("button_id") or value.get("callback_data")
                    if button_id:
                        break

        if not button_id:
            return False

        if self.regex:
            return bool(self.button_id.match(button_id))
        else:
            return button_id == self.button_id


class forward(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            if bool(update.find_key("forwarded_no_link")):
                return True
            return bool(update.find_key("forwarded_from"))

        except KeyError:
            return False


class is_edited(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("is_edited"))

        except KeyError:
            return False


class sender_type(Filter):
    def __init__(self, types: Union[List[str], str]):
        self.types = [types] if isinstance(types, str) else types

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            sender_type = update.find_key("sender_type")
            return bool(sender_type in self.types)
        except KeyError:
            return False


class has_aux_data(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("aux_data"))

        except KeyError:
            return False


class file(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("file"))

        except KeyError:
            return False

class photo(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            result = update.find_key("file")
            if result:
                result = mimetypes.guess_type(result.file_name)[0]
                if result:
                    return result.startswith("image/")
            return result

        except KeyError:
            return False

class video(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            result = update.find_key("file")
            if result:
                result = mimetypes.guess_type(result.file_name)[0]
                if result:
                    return result.startswith("video/")
            return result

        except KeyError:
            return False

class audio(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            result = update.find_key("file")
            if result:
                result = mimetypes.guess_type(result.file_name)[0]
                if result:
                    return result.startswith("audio/") and not result.endswith("ogg")
            return result

        except KeyError:
            return False

class voice(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            result = update.find_key("file")
            if result:
                result = mimetypes.guess_type(result.file_name)[0]
                if result:
                    return result == "audio/ogg"
            return result

        except KeyError:
            return False

class gif(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            result = update.find_key("file")
            if result:
                result = mimetypes.guess_type(result.file_name)[0]
                if result:
                    return result.endswith("gif")
            return result

        except KeyError:
            return False

class location(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("location"))

        except KeyError:
            return False


class sticker(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("sticker"))

        except KeyError:
            return False


class contact_message(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("contact_message"))

        except KeyError:
            return False


class poll(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("poll"))

        except KeyError:
            return False


class live_location(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        try:
            return bool(update.find_key("live_location"))

        except KeyError:
            return False


class replied(Filter):
    async def check(self, update):
        try:
            return bool(update.find_key("reply_to_message_id"))
        except KeyError:
            return False

class metadata(Filter):
    async def check(self, update):
        try:
            return bool(update.find_key("metadata"))
        except KeyError:
            return False

class states(Filter):
    _STORE: Dict[str, str] = {}
    _TTL_TASKS: Dict[str, asyncio.Task] = {}

    def __init__(
        self,
        targets: Optional[Union[str, List[str]]] = None,
        match_mode: str = "exact",
        scope: str = "user",
        check_keys: Optional[List[str]] = None,
        auto_clear: bool = False,
        set_on_match: Optional[str] = None,
        expire: Optional[int] = None,
        invert: bool = False,
    ):
        self.targets = [targets] if isinstance(targets, str) else (targets or None)
        assert match_mode in ("exact", "regex", "contains", "any")
        assert scope in ("user", "chat", "both")
        self.match_mode = match_mode
        self.scope = scope
        self.check_keys = check_keys or [
            "state",
            "fsm_state",
            "user_state",
            "session_state",
        ]
        self.auto_clear = auto_clear
        self.set_on_match = set_on_match
        self.default_expire = expire
        self.invert = invert

        if self.match_mode == "regex" and self.targets:
            self._patterns = [re.compile(p) for p in self.targets]
        else:
            self._patterns = None

    @classmethod
    async def _schedule_expiry(cls, key: str, seconds: int):
        old = cls._TTL_TASKS.get(key)
        if old and not old.done():
            old.cancel()

        async def _job():
            try:
                await asyncio.sleep(seconds)
                cls._STORE.pop(key, None)
                cls._TTL_TASKS.pop(key, None)
            except asyncio.CancelledError:
                return

        t = asyncio.create_task(_job())
        cls._TTL_TASKS[key] = t

    @classmethod
    async def _set_store(cls, key: str, value: str, expire: Optional[int] = None):
        cls._STORE[key] = value
        if expire:
            await cls._schedule_expiry(key, expire)

    @classmethod
    async def _get_store(cls, key: str) -> Optional[str]:
        return cls._STORE.get(key)

    @classmethod
    async def _clear_store(cls, key: str):
        cls._STORE.pop(key, None)
        task = cls._TTL_TASKS.pop(key, None)
        if task and not task.done():
            task.cancel()

    async def set_state_for(
        self,
        update: Union[Update, InlineMessage, Any],
        value: str,
        expire: Optional[int] = None,
    ):
        klist = self._keys_for_update(update)
        if not klist:
            raise RuntimeError("Cannot determine key from update to set state")
        for k in klist:
            await self._set_store(k, value, expire or self.default_expire)

    async def get_state_for(
        self, update: Union[Update, InlineMessage, Any]
    ) -> Optional[str]:
        klist = self._keys_for_update(update)
        if not klist:
            return None
        for k in klist:
            v = await self._get_store(k)
            if v is not None:
                return v
        return None

    async def clear_state_for(self, update: Union[Update, InlineMessage, Any]):
        klist = self._keys_for_update(update)
        if not klist:
            return
        for k in klist:
            await self._clear_store(k)

    def _keys_for_update(self, update: Union[Update, InlineMessage, Any]) -> List[str]:
        keys = []
        sender_id = getattr(update, "sender_id", None)
        chat_id = getattr(update, "chat_id", None)
        try:
            if not sender_id and hasattr(update, "find_key"):
                sender_id = (
                    update.find_key("sender_id")
                    or update.find_key("from_id")
                    or sender_id
                )
        except Exception:
            pass
        try:
            if not chat_id and hasattr(update, "find_key"):
                chat_id = update.find_key("chat_id") or chat_id
        except Exception:
            pass

        if self.scope in ("user", "both") and sender_id:
            keys.append(f"user:{sender_id}")
        if self.scope in ("chat", "both") and chat_id:
            keys.append(f"chat:{chat_id}")
        return keys

    async def _extract_local_state(
        self, update: Union[Update, InlineMessage, Any]
    ) -> Optional[str]:
        for k in self.check_keys:
            try:
                if hasattr(update, "find_key"):
                    val = update.find_key(k)
                else:
                    val = getattr(update, k, None)
            except Exception:
                val = None
            if val:
                if isinstance(val, (list, tuple, set)):
                    val = next((x for x in val if isinstance(x, str)), None)
                if isinstance(val, (str, int, float)):
                    return str(val)
        try:
            aux = (
                update.find_key("aux_data")
                if hasattr(update, "find_key")
                else getattr(update, "aux_data", None)
            )
            if aux and isinstance(aux, dict):
                for k in ("state", "fsm_state"):
                    v = aux.get(k)
                    if v:
                        return str(v)
        except Exception:
            pass
        return None

    def _matches(self, value: str) -> bool:
        if self.match_mode == "any":
            return True if value else False
        if self.match_mode == "contains":
            return any(t in value for t in (self.targets or []))
        if self.match_mode == "regex" and self._patterns:
            return any(p.match(value) for p in self._patterns)
        return value in (self.targets or [])

    async def check(self, update: Union[Update, InlineMessage, Any]) -> bool:
        local = await self._extract_local_state(update)
        state_val = None
        if local:
            state_val = local

        if state_val is None:
            state_val = await self.get_state_for(update)

        matched = False if state_val is None else self._matches(state_val)

        matched = (not matched) if self.invert else matched

        if matched:
            if self.auto_clear:
                await self.clear_state_for(update)
            if self.set_on_match:
                await self.set_state_for(
                    update, self.set_on_match, expire=self.default_expire
                )

        return matched
