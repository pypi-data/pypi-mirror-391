import aiohttp
import asyncio
import inspect
import time
import platform
import orjson
import aiodns
from typing import List, Optional, Dict, Any, Literal, Callable, Awaitable, Union
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os

from .exceptions import APIRequestError
from .logger import logger
from .update import Message, InlineMessage  # Import from update.py instead
from collections import deque
from pathlib import Path


API_URL = "https://botapi.rubika.ir/v3"

class InvalidTokenError(Exception):
    """Raised when the provided bot token is invalid or expired."""
    pass

class Robot:
    """High-performance Rubika Bot API implementation."""
    
    def __init__(self, token: str):
        self.token = token
        # Cached getMe response (populated by _validate_token)
        self._me: Optional[Dict[str, Any]] = None
        self._offset_id = None
        self.session: Optional[aiohttp.ClientSession] = None
        # support multiple message handlers (preserve registration order)
        self._message_handlers: List[Dict[str, Any]] = []
        self._edited_message_handler: Optional[Dict[str, Any]] = None
        self._inline_query_handler: Optional[Callable[[Any, InlineMessage], Awaitable[None]]] = None 
        self._started_bot_handler: Optional[Callable[[Any, Any], Awaitable[None]]] = None 
        self._stopped_bot_handler: Optional[Callable[[Any, Any], Awaitable[None]]] = None 
        self._on_callback_handler: Dict[str, Callable] = {} 
        self.offset_file = f"offset_{self.token[:10]}.txt"
        
        # High performance optimizations
        # Keep thread pool tiny on low-memory/single-core hosts
        self._thread_pool = ThreadPoolExecutor(max_workers=1)  # For CPU-bound tasks
        self._upload_semaphore = asyncio.Semaphore(10)  # Limit concurrent uploads
        self._request_semaphore = asyncio.Semaphore(100)  # Rate limiting
        self._backoff = 1.0  # Initial backoff time
        
        # Connection optimization
        # Defer creating the aiohttp.TCPConnector until an event loop is running.
        # aiohttp's connector may try to access the running loop during init on
        # newer Python versions, which raises if no loop is running. Store the
        # connector kwargs and create the connector inside `run()` where an
        # event loop is guaranteed to exist.
        self._tcp_connector = None
        self._connector_kwargs = {
            "limit": 100,  # Max concurrent connections
            # limit_per_host can be set when actually creating the connector
            "ttl_dns_cache": 300,  # DNS cache TTL
            "use_dns_cache": True,
            "ssl": False,  # Internal API, no SSL needed
            "enable_cleanup_closed": True,  # Clean up closed connections
        }
        
        # Session settings
        self._timeout = aiohttp.ClientTimeout(total=300)  # 5 min timeout
        def _orjson_dumps_str(obj):
            return orjson.dumps(obj).decode("utf-8")
        self._session_params = {
            "timeout": self._timeout,
            "connector": self._tcp_connector,
            "json_serialize": _orjson_dumps_str,  # Return str, not bytes
            "raise_for_status": True,
            "trace_configs": None  # Disable tracing for performance
        }
        
        # Message processing
        # Make dedupe window configurable via env for low-memory hosts
        dedupe_max = int(os.environ.get('RUBIKA_DEDUPE_MAX', '10000'))
        self.processed_messages = deque(maxlen=dedupe_max)  # Message deduplication
        self.running = False
        self.first_get_updates = True
        self._token_validated = False
        # Webhook mode and per-chat ordering
        # If webhook_mode is True, user will call `await bot.handle_webhook_update(update)`
        # to hand updates from their web framework (aiohttp/fastapi/etc.).
        self.webhook_mode: bool = False
        # Locks per chat to keep per-chat sequential processing while allowing high concurrency
        self._chat_locks: Dict[str, asyncio.Lock] = {}
        # Track inflight tasks optionally to await on shutdown if desired
        self._inflight_tasks: Dict[asyncio.Task, str] = {}
        # Middleware and handlers
        self.middlewares: List[Callable] = []
        self.start_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []

        # Concurrency tuning
        # Max concurrent handler tasks allowed to run at once. Read from env
        # so users can tune for their environment without changing code.
        try:
            env_max = int(os.environ.get('RUBIKA_MAX_HANDLERS', '500'))
        except Exception:
            env_max = 500
        # clamp to reasonable bounds
        self.max_concurrent_handlers = max(10, min(env_max, 2000))
        self._handler_semaphore = asyncio.Semaphore(self.max_concurrent_handlers)

        # Rate limiting
        self.rate_limit = 0.05  # 50ms between requests
        self.last_request_time = 0

        logger.info(f"Starting ON offset: {self._read_offset()}")
    
    async def _validate_token(self):
        """Validate the bot token by calling getMe (async)."""
        if self._token_validated:
            return self._me
        try:
            if not self.session:
                # Create temporary session for validation
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as temp_session:
                    url = f"{API_URL}/{self.token}/getMe"
                    async with temp_session.post(url, json={}) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get('status') != "OK":
                            raise InvalidTokenError("The provided bot token is invalid or expired.")
                        # Cache getMe data for later use by run() before session exists
                        self._me = result.get('data', {})
            else:
                result = await self._post("getMe", {})
                if result.get('status') != "OK":
                    raise InvalidTokenError("The provided bot token is invalid or expired.")
                self._me = result.get('data', {})
            self._token_validated = True
        except Exception as e:
            if isinstance(e, InvalidTokenError):
                raise
            logger.warning(f"Could not validate token: {e}")
            return None
        return self._me

    def _read_offset(self) -> Optional[str]:
        try:
            with open(self.offset_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError: return None

    def _save_offset(self, offset_id: str):
        with open(self.offset_file, "w") as f:
            f.write(str(offset_id))

    async def _rate_limit_delay(self):
        """Rate limiting for high performance - prevents API throttling"""
        # use monotonic clock to avoid issues with system clock adjustments
        now = time.monotonic()
        elapsed = now - getattr(self, 'last_request_time', now)
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self.last_request_time = now

    async def _post(self, method: str, data: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
        """Optimized API request handler."""
        if not self.session:
            raise RuntimeError("Bot session not running. Use 'await bot.run()'.")
        
        # Efficient rate limiting with semaphore
        async with self._request_semaphore:
            await self._rate_limit_delay()
            
            url = f"{API_URL}/{self.token}/{method}"
            retries = 3
            last_error = None
            
            for attempt in range(retries):
                try:
                    async with self.session.post(
                        url,
                        json=data,
                        timeout=timeout,
                        headers={"Accept-Encoding": "br,gzip,deflate"},
                        compress=False  # Let aiohttp handle compression
                    ) as response:
                        try:
                            # Parse JSON in thread pool to avoid blocking event loop
                            json_str = await response.text()
                            json_resp = await asyncio.get_event_loop().run_in_executor(
                                self._thread_pool,
                                orjson.loads,
                                json_str
                            )
                            
                            # Fast path for successful responses
                            if json_resp.get("status") == "OK":
                                if method != "getUpdates":
                                    logger.debug(f"API Response from {method}: {json_resp}")
                                return json_resp
                                
                            raise APIRequestError(f"API error: {json_resp.get('status_det', 'Unknown error')}")
                            
                        except orjson.JSONDecodeError:
                            logger.error(f"Invalid JSON from {method}: {json_str[:1000]}")
                            raise APIRequestError(f"Invalid JSON response")
                            
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_error = e
                    if attempt < retries - 1:
                        # Exponential backoff
                        await asyncio.sleep(self._backoff * (2 ** attempt))
                        continue
                    logger.error(f"Request failed after {retries} retries: {e}")
                    raise APIRequestError(f"Request failed: {e}") from e

            if last_error:
                raise APIRequestError(f"Max retries exceeded: {last_error}")

    def on_message(self, filters: Optional[Callable[[Message], bool]] = None, commands: Optional[List[str]] = None):
        def decorator(func: Callable[[Any, Message], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The message handler function must be a coroutine (using async def).")
            # Append handler info so multiple handlers can coexist.
            self._message_handlers.append({
                "func": func,
                "filters": filters,
                "commands": commands
            })
            return func
        return decorator

    def on_edited_message(self, filters: Optional[Callable[[Message], bool]] = None):
        def decorator(func: Callable[[Any, Message], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The edited message handler function must be a coroutine (using async def).")
            self._edited_message_handler = {
                "func": func,
                "filters": filters
            }
            return func
        return decorator

    def on_inline_query(self): 
        def decorator(func: Callable[[Any, InlineMessage], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The inline query handler function must be a coroutine (using async def).")
            self._inline_query_handler = func
            return func
        return decorator

    def on_started_bot(self): 
        def decorator(func: Callable[[Any, Any], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The bot started handler function must be a coroutine (using async def).")
            self._started_bot_handler = func
            return func
        return decorator

    def on_stopped_bot(self):
        """
        Decorator to register a function that will be called when the bot is stopped.
    
        The decorated function must be an asynchronous function (defined using `async def`).
        It should accept two positional arguments, which will be provided by the event
        that triggers the stop handler.
    
        Raises:
            TypeError: If the decorated function is not a coroutine.
        """
    
        def decorator(func: Callable[[Any, Any], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The bot stopped handler function must be a coroutine (using async def).")
            self._stopped_bot_handler = func
            return func
        return decorator

    def on_start(self):
        """Decorator to register startup handlers."""
        def decorator(func: Callable):
            self.start_handlers.append(func)
            return func
        return decorator

    def on_shutdown(self):
        """Decorator to register shutdown handlers."""
        def decorator(func: Callable):
            self.shutdown_handlers.append(func)
            return func
        return decorator

    def middleware(self):
        """
        Decorator to register a middleware function.
        
        Middleware receives (bot, update, next_middleware).
        It must call `await next_middleware()` to continue chain.
        """
        def decorator(func: Callable):
            self.middlewares.append(func)
            logger.info(f"Middleware {func.__name__} registered")
            return func
        return decorator

    # New: Decorator for on_callback (similar to rubka)
    def on_callback(self, button_id: str) -> Callable:
        """Decorator to register a function that will be called when a button with the specified ID is clicked.

        The decorated function must be an asynchronous function (defined using `async def`).
        It should accept one positional argument, a `Message` object, which will be the message context of the button click event.

        Args:
            button_id: The unique ID of the button to be handled. This ID should match the value passed to `button_id` when creating the button.

        Raises:
            TypeError: If the decorated function is not a coroutine.
        """

        def decorator(func: Callable[[Any, Message], Awaitable[None]]): # Changed to Message context for uniformity
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Callback handler must be a coroutine (using async def).")
            self._on_callback_handler[button_id] = func
            return func
        return decorator

    def _is_duplicate(self, message_id: str, max_age_sec: int = 300) -> bool:
        """Check if message was already processed (for performance)"""
        if message_id in self.processed_messages:
            return True
        self.processed_messages.append(message_id)
        return False

    def _extract_text_from_msg(self, msg: Dict[str, Any]) -> Optional[str]:
        """Try several common locations for message text in incoming update payloads.

        Rubika variants sometimes embed text under different keys (text, message.text,
        content.text, caption, body). This helper centralizes fallbacks so handlers
        see the expected `text` value.
        """
        if not msg or not isinstance(msg, dict):
            return None

        # Quick direct fields
        for key in ('text', 'message_text', 'body', 'caption'):
            val = msg.get(key)
            if val:
                return val

        # Walk a few common nested paths used by different Rubika clients
        nested_candidates = []
        if isinstance(msg.get('message'), dict):
            nested_candidates.append(msg.get('message'))
        if isinstance(msg.get('content'), dict):
            nested_candidates.append(msg.get('content'))

        # Some payloads nest message->message->text, so descend up to 3 levels
        def find_text_in(obj, depth=0):
            if depth > 3 or not isinstance(obj, dict):
                return None
            for k in ('text', 'body', 'caption', 'message_text'):
                if k in obj and obj[k]:
                    return obj[k]
            # some payloads put text under 'message' or 'content' keys
            for child_key in ('message', 'content'):
                child = obj.get(child_key)
                if isinstance(child, dict):
                    found = find_text_in(child, depth + 1)
                    if found:
                        return found
            return None

        for candidate in nested_candidates:
            t = find_text_in(candidate)
            if t:
                return t

        # Last-resort: search shallowly for any string field that looks like text
        for k, v in msg.items():
            if isinstance(v, str) and len(v) > 0 and '\n' not in v and len(v) < 4096:
                # avoid returning IDs or long blobs; prefer short text-like strings
                if v.strip().startswith('/') or len(v.split()) < 200:
                    return v

        return None

    def _has_time_passed(self, last_time: Optional[str], seconds: int = 5) -> bool:
        """Check if message is too old (skip old messages for performance)"""
        if not last_time:
            return False
        try:
            timestamp = int(float(last_time))
            now = time.time()
            return (now - timestamp) > seconds
        except (TypeError, ValueError):
            return False

    async def _run_middlewares(self, update: Dict[str, Any], index: int = 0):
        """Run middleware chain for high performance processing."""
        if index < len(self.middlewares):
            mw = self.middlewares[index]
            async def next_middleware():
                await self._run_middlewares(update, index + 1)
            
            if inspect.iscoroutinefunction(mw):
                await mw(self, update, next_middleware)
            else:
                # Run sync middleware in a thread so it can't block the event loop
                await asyncio.to_thread(mw, self, update, next_middleware)
        else:
            await self._process_update(update)

    def _schedule_coroutine(self, coro: Awaitable) -> asyncio.Task:
        """Schedule a coroutine while respecting the handler semaphore.

        Wrap the coroutine to acquire the handler semaphore so we don't
        spawn an unbounded number of concurrent handler executions that
        could exhaust memory or connections. Returns the created Task.
        """
        async def _runner():
            async with self._handler_semaphore:
                try:
                    await coro
                except Exception as e:
                    logger.error(f"Handler task exception: {e}")

        return asyncio.create_task(_runner())

    async def _call_handler(self, func: Callable, context: Message):
        """Call handler `func` with graceful backwards-compatible argument mapping.

        Supports handlers of the form:
          async def handler(bot, context)
        or
          async def handler(bot, chat_id, message_id, text, sender_id)

        Falls back to calling with (bot, context) if signature doesn't match.
        """
        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.values())

            # Expect first param to be the bot; remaining params decide call style.
            if len(params) == 2:
                # (bot, context)
                await func(self, context)
                return

            # If handler expects 5+ params assume legacy (bot, chat_id, message_id, text, sender_id)
            if len(params) >= 5:
                try:
                    await func(self, context.chat_id, context.message_id, context.text, context.sender_id)
                    return
                except TypeError:
                    # Fallthrough to try calling with context
                    pass

            # Fallback: try calling with (bot, context)
            await func(self, context)
        except Exception as e:
            logger.error(f"Error while invoking handler {getattr(func, '__name__', repr(func))}: {e}")

    async def _process_update(self, update: Dict[str, Any]):
        event_type = update.get('type')
        
        if event_type == 'NewMessage':
            # Check for specific button callbacks first (on_callback decorator)
            msg = update.get("new_message", {})
            message_id = str(msg.get('message_id', ''))
            
            # Skip duplicates for performance
            if self._is_duplicate(message_id):
                return
            
            # Skip old messages (performance optimization)
            if self._has_time_passed(msg.get('time'), seconds=5):
                return
            
            if msg.get('aux_data') and msg['aux_data'].get('button_id'):
                button_id = msg['aux_data']['button_id']
                if button_id in self._on_callback_handler:
                    context = Message(bot=self, chat_id=update.get('object_guid') or update.get('chat_id'),
                                      message_id=message_id, sender_id=msg.get('sender_id'),
                                      text=msg.get('text'), raw_data=msg)
                    # Schedule callback handler through the handler semaphore (compat wrapper)
                    self._schedule_coroutine(self._call_handler(self._on_callback_handler[button_id], context))
                    return # Handle callback, don't pass to general message handler

            # If not a callback, proceed to general message handler(s)
            if self._message_handlers:
                chat_id = update.get('object_guid') or update.get('chat_id')
                if not chat_id: return
                text_val = self._extract_text_from_msg(msg)
                context = Message(bot=self, chat_id=chat_id, message_id=message_id,
                                  sender_id=msg.get('sender_id'), text=text_val, raw_data=msg)

                # Iterate registered handlers in order. Command handlers consume the update.
                for handler_info in list(self._message_handlers):
                    # Check filters (async-aware)
                    filters = handler_info.get("filters")
                    if filters:
                        if inspect.iscoroutinefunction(filters):
                            try:
                                ok = await filters(context)
                            except Exception as e:
                                logger.error(f"Filter error: {e}")
                                continue
                        else:
                            try:
                                ok = filters(context)
                            except Exception as e:
                                logger.error(f"Filter error: {e}")
                                continue
                        if not ok:
                            continue

                    commands = handler_info.get("commands")
                    if commands:
                        if not context.text or not context.text.startswith("/"):
                            continue
                        parts = context.text.split()
                        cmd = parts[0][1:]
                        if cmd not in commands:
                            continue
                        context.args = parts[1:] if len(parts) > 1 else []
                        # Schedule and consume the update
                        self._schedule_coroutine(self._call_handler(handler_info["func"], context))
                        break
                    else:
                        # Non-command handler: schedule but don't consume, allow others to run
                        self._schedule_coroutine(self._call_handler(handler_info["func"], context))
        
        elif event_type == 'UpdatedMessage':
            if self._edited_message_handler:
                msg = update.get("updated_message", {})
                chat_id = update.get('object_guid') or update.get('chat_id')
                if not chat_id: return

                context = Message(
                    bot=self,
                    chat_id=chat_id,
                    message_id=msg.get('message_id'),
                    sender_id=msg.get('sender_id'),
                    text=msg.get('text'),
                    raw_data=msg
                )
                await self._call_handler(self._edited_message_handler["func"], context)
        elif event_type == 'ReceiveQuery': 
             if self._inline_query_handler:
                msg = update.get("inline_message", {})
                context = InlineMessage(bot=self, raw_data=msg)
                await self._inline_query_handler(self, context)
                return
        elif event_type == 'StartedBot' and self._started_bot_handler:
            chat_id = update.get('chat_id') 
            await self._started_bot_handler(self, chat_id)
        elif event_type == 'StoppedBot' and self._stopped_bot_handler:
            chat_id = update.get('chat_id')
            await self._stopped_bot_handler(self, chat_id)
        elif event_type == 'RemovedMessage':
            removed_id = update.get('removed_message_id')
            logger.info(f"Message {removed_id} was removed in a chat.")
        else:
            logger.debug(f"Received an unhandled event type: {event_type}")

    async def run(self, mode: str = 'polling'):
        """Ultra high-performance bot runtime implementation."""
        # Validate token first — fail fast if the token is invalid.
        # Wrap the run loop so that CancelledError is handled by the
        # outer session/polling block and doesn't propagate to callers
        # awaiting the run task. Validate token up-front so we fail-fast
        # on invalid tokens.
        me = await self._validate_token()

        # mode: 'polling' (default) or 'webhook'
        if mode not in ('polling', 'webhook'):
            raise ValueError("mode must be 'polling' or 'webhook')")
        self.webhook_mode = (mode == 'webhook')
        logger.info(f"Bot run mode: {mode}")

        # Print a short summary of the bot we're connected to so the user
        # immediately knows which bot/account this process is operating as.
        try:
            if me:
                bot_info = me.get('bot') if isinstance(me, dict) and 'bot' in me else me
                bot_id = bot_info.get('bot_id') if isinstance(bot_info, dict) else None
                bot_title = bot_info.get('bot_title') if isinstance(bot_info, dict) else None
                username = bot_info.get('username') if isinstance(bot_info, dict) else None
                share = bot_info.get('share_url') if isinstance(bot_info, dict) else None
                print(f"YOUR BOT: {bot_title or '<unknown>'} (@{username or 'unknown'}) — id={bot_id}")

                
        except InvalidTokenError:
            # Validation already logged; re-raise so the run will stop.
            raise
        except Exception as e:
            logger.warning(f"Could not format getMe info at startup: {e}")

        print("🟢 BOT IS WAKING UP ✅")

        # Initialize core components
        self._offset_id = self._read_offset()
        self.running = True

        # Run start handlers in parallel
        start_tasks = [
            handler(self) if inspect.iscoroutinefunction(handler) else asyncio.to_thread(handler, self)
            for handler in self.start_handlers
        ]
        if start_tasks:
            await asyncio.gather(*start_tasks)
        
        # Optimal connection settings
        # Create the connector now that we are inside an event loop.
        connector_kwargs = dict(self._connector_kwargs)
        # Update runtime-specific defaults for the run() context
        connector_kwargs.update({
            "limit": 200,
            "limit_per_host": 50,
            # keep ttl_dns_cache, use_dns_cache, ssl, enable_cleanup_closed from stored kwargs
        })
        connector = aiohttp.TCPConnector(**connector_kwargs)
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        # Use orjson for maximum JSON performance
        def _orjson_dumps_str(obj):
            return orjson.dumps(obj).decode("utf-8")
        session_params = {
            "timeout": timeout,
            "connector": connector,
            "json_serialize": _orjson_dumps_str,
            "raise_for_status": True,
            "trace_configs": None
        }
        
        try:
            async with aiohttp.ClientSession(**session_params) as session:
                self.session = session
                print("OFFSET UPDATED . LISTENING FOR NEW MESSAGES ♻")

                # If webhook mode is enabled, we do not poll getUpdates.
                if self.webhook_mode:
                    logger.info("Running in webhook mode: not polling. Use handle_webhook_update(update) from your web server.")
                    try:
                        # Simple wait loop, keep the session open and let external web handler call handle_webhook_update
                        while self.running:
                            await asyncio.sleep(0.5)
                    finally:
                        # On exit, proceed to shutdown as usual
                        pass

                # Clear old messages (only relevant for polling)
                if not self.webhook_mode:
                    if self.first_get_updates:
                        await self.get_updates(offset_id=self._offset_id, limit=100)
                        self.first_get_updates = False

                    # Use a bounded queue to avoid unbounded memory growth on low-RAM hosts.
                    update_queue = asyncio.Queue(maxsize=2000)
                    process_pool = []

                    # Conservative worker count tuned for single-core / low-memory hosts.
                    # For 1 CPU this yields 2 workers; raise `worker_count` on bigger machines.
                    worker_count = min(max((os.cpu_count() or 1) * 2, 2), 8)
                    for _ in range(worker_count):
                        task = asyncio.create_task(self._process_update_worker(update_queue))
                        process_pool.append(task)

                    try:
                        backoff = 0.1  # Initial backoff
                        max_backoff = 5.0  # Max backoff time

                        while self.running:
                            try:
                                # Efficient update polling
                                updates = await self.get_updates(
                                    offset_id=self._offset_id,
                                    limit=100  # Get more updates at once
                                )

                                if updates and (data := updates.get('data')):
                                    if update_list := data.get('updates', []):
                                        # Reset backoff on success
                                        backoff = 0.1

                                        # Push updates into the bounded queue. If the queue is full
                                        # the producer will block briefly which acts as backpressure.
                                        for update in update_list:
                                            await update_queue.put(update)

                                    # Update offset (prefer provided next_offset_id, fallback to last message id)
                                    if next_offset := data.get('next_offset_id'):
                                        self._offset_id = next_offset
                                        self._save_offset(next_offset)
                                    else:
                                        # Defensive fallback: use last message_id from the batch
                                        last_msg_id = None
                                        for u in update_list:
                                            m = u.get('new_message') or u.get('updated_message') or {}
                                            mid = m.get('message_id') or u.get('message_id') or None
                                            if mid:
                                                last_msg_id = str(mid)
                                        if last_msg_id:
                                            self._offset_id = last_msg_id
                                            self._save_offset(last_msg_id)

                                    # Adaptive polling rate
                                    if len(update_list) < 10:
                                        await asyncio.sleep(0.1)  # Light load
                                    else:
                                        await asyncio.sleep(0.01)  # Heavy load, poll faster

                                else:
                                    # Exponential backoff when no updates
                                    backoff = min(backoff * 1.5, max_backoff)
                                    await asyncio.sleep(backoff)

                            except Exception as e:
                                logger.error(f"Update loop error: {e}")
                                backoff = min(backoff * 2, max_backoff)
                                await asyncio.sleep(backoff)

                    finally:
                        # Graceful shutdown
                        self.running = False

                        # Cancel processors
                        for task in process_pool:
                            task.cancel()

                        await asyncio.gather(*process_pool, return_exceptions=True)

                        # Run shutdown handlers
                        shutdown_tasks = [
                            handler(self) if inspect.iscoroutinefunction(handler) else asyncio.to_thread(handler, self)
                            for handler in self.shutdown_handlers
                        ]
                        if shutdown_tasks:
                            await asyncio.gather(*shutdown_tasks)
        except asyncio.CancelledError:
            # External cancellation requested (cancelled task). Try to stop
            # gracefully and swallow the CancelledError so callers awaiting
            # the run task don't see a traceback.
            logger.info("Run task cancelled; shutting down gracefully.")
            self.running = False
            try:
                await self.stop()
            except Exception as e:
                logger.warning(f"Error during shutdown after cancellation: {e}")
            return
    async def _process_update_worker(self, queue: asyncio.Queue):
        """Dedicated update processing worker."""
        while True:
            try:
                update = await queue.get()
                # Process middlewares inline in the worker to avoid creating
                # many short-lived Task objects. This reduces memory and
                # scheduling overhead on low-resource hosts.
                try:
                    await self._run_middlewares(update)
                finally:
                    queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Update processing error: {e}")
                await asyncio.sleep(0.1)

    async def _process_update_with_lock(self, update: Dict[str, Any]):
        """Process single update but ensure per-chat sequential ordering.

        For messages belonging to the same chat, this function will acquire a
        per-chat asyncio.Lock so only one handler runs at a time per chat.
        This enables high concurrency across chats while preserving order
        and avoiding race conditions for chat-scoped state.
        """
        # Determine chat identifier (fall back to sender/chat fields)
        chat_id = update.get('object_guid') or update.get('chat_id')
        # For messages, prefer object_guid; otherwise use a generic key
        if not chat_id:
            # Use a global lock key for updates that don't belong to a chat
            chat_id = '_global'

        # Create lock if necessary
        lock = self._chat_locks.get(chat_id)
        if lock is None:
            lock = asyncio.Lock()
            self._chat_locks[chat_id] = lock

        # Acquire lock and process
        async with lock:
            try:
                await self._run_middlewares(update)
            except Exception as e:
                logger.error(f"Error processing update for chat {chat_id}: {e}")

    async def handle_webhook_update(self, update: Dict[str, Any]):
        """Entry point for webhook-based frameworks.

        Call this from your web handler (FastAPI/Aiohttp/Quart) when an
        incoming update is received. The call will schedule processing as a
        bounded task using the existing handler semaphore and per-chat locks
        to preserve ordering per chat while allowing concurrency across chats.

        Example (FastAPI):
            @app.post('/webhook')
            async def webhook(req: Request):
                update = await req.json()
                await bot.handle_webhook_update(update)
                return JSONResponse({'ok': True})
        """
        # Quick duplicate filter
        try:
            msg = update.get('new_message') or update.get('updated_message') or update.get('inline_message')
            message_id = str((msg or {}).get('message_id', '') or (update.get('id') or ''))
            if message_id and self._is_duplicate(message_id):
                return
        except Exception:
            # If anything goes wrong extracting message id, continue to process
            pass

        # Use handler semaphore to bound concurrent handlers
        async def _coro():
            async with self._handler_semaphore:
                try:
                    await self._process_update_with_lock(update)
                except Exception as e:
                    logger.error(f'Unhandled exception in webhook update processing: {e}')

        task = asyncio.create_task(_coro())
        # track task optionally
        self._inflight_tasks[task] = 'webhook'
        # remove tracking when done
        def _done_cb(t: asyncio.Task):
            try:
                self._inflight_tasks.pop(t, None)
            except Exception:
                pass

        task.add_done_callback(_done_cb)
        # return quickly so web server can reply
        return

    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Optional[Dict[str, Any]] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: Optional[Any] = None, 
        auto_delete: Optional[float] = None,
        retry_count: int = 3,
        backoff_factor: float = 1.5
    ) -> Dict[str, Any]:
        # Build optimized payload with only needed fields
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": disable_notification,
            **({"chat_keypad": chat_keypad} if chat_keypad else {}),
            **({"inline_keypad": inline_keypad} if inline_keypad else {}),
            **({"reply_to_message_id": reply_to_message_id} if reply_to_message_id else {}),
            **({"chat_keypad_type": chat_keypad_type.value if hasattr(chat_keypad_type, 'value') else chat_keypad_type} if chat_keypad_type else {})
        }

        last_error = None
        for attempt in range(retry_count):
            try:
                result = await self._post("sendMessage", payload)
                
                # Handle auto-delete efficiently 
                if auto_delete and result:
                    if msg_id := result.get('data', {}).get('message_update', {}).get('message_id'):
                        # Use background task for auto-delete
                        asyncio.create_task(
                            self.auto_delete_message(
                                chat_id=chat_id,
                                message_id=msg_id,
                                delay=auto_delete
                            )
                        )
                return result
                
            except Exception as e:
                last_error = e
                if attempt < retry_count - 1:
                    # Exponential backoff
                    await asyncio.sleep(backoff_factor * (2 ** attempt))
                    continue
                    
        # If we get here, all retries failed
        raise APIRequestError(f"Failed to send message after {retry_count} attempts: {last_error}")

    async def auto_delete_message(self, chat_id: str, message_id: str, delay: float):
        await asyncio.sleep(delay)
        try:
            await self.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.warning(f"Could not auto-delete message {message_id}: {e}")

    async def send_poll(
        self,
        chat_id: str,
        question: str,
        options: List[str],
        type: Literal["Regular", "Quiz"] = "Regular",
        allows_multiple_answers: bool = False,
        is_anonymous: bool = True,
        correct_option_index: Optional[int] = None,
        explanation: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad: Optional[Dict[str, Any]] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send a poll with advanced options."""
        payload = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "type": type,
            "allows_multiple_answers": allows_multiple_answers,
            "is_anonymous": is_anonymous,
            "disable_notification": disable_notification,
        }
        if correct_option_index is not None:
            payload["correct_option_index"] = correct_option_index
        if explanation:
            payload["explanation"] = explanation
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendPoll", payload)

    async def send_location(self, chat_id: str, latitude: str, longitude: str, disable_notification: bool = False, inline_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, chat_keypad_type: Optional[Literal["New", "Removed"]] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, "disable_notification": disable_notification, "inline_keypad": inline_keypad, "reply_to_message_id": reply_to_message_id, "chat_keypad_type": chat_keypad_type}
        payload = {k: v for k, v in payload.items() if v is not None}
        return await self._post("sendLocation", payload)

    async def send_contact(self, chat_id: str, first_name: str, last_name: str, phone_number: str, chat_keypad: Optional[Dict[str, Any]] = None, inline_keypad: Optional[Dict[str, Any]] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "phone_number": phone_number, "disable_notification": disable_notification}
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendContact", payload)

    async def get_chat(self, chat_id: str) -> Dict[str, Any]:
        return await self._post("getChat", {"chat_id": chat_id})

    # New method: get_me (from rubpy)
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information."""
        result = await self._post("getMe", {})
        return result.get("data", {})

    # New method: get_name (based on rubka)
    async def get_name(self, user_id: str) -> Optional[str]:
        """Gets the first name of a user from their user_id."""
        try:
            chat_info_response = await self.get_chat(user_id)
            chat_data = chat_info_response.get("data", {}).get("chat", {})
            first_name = chat_data.get("first_name", "")
            last_name = chat_data.get("last_name", "")
            if first_name and last_name:
                return f"{first_name} {last_name}"
            return first_name or last_name or "Unknown"
        except Exception:
            return "Unknown"

    # New method: get_username (based on rubka)
    async def get_username(self, user_id: str) -> Optional[str]:
        """Gets the username of a user from their user_id."""
        try:
            chat_info_response = await self.get_chat(user_id)
            return chat_info_response.get("data", {}).get("chat", {}).get("username", "None")
        except Exception:
            return "None"

    # New method: check_join (placeholder for rubka)
    async def check_join(self, chat_id: str, user_id: str) -> bool:
        """Try to check if `user_id` is member of `chat_id` using an adaptor client when available.

        Falls back to simple False when not available.
        """
        # Try using BotClient Client if present for more advanced member queries
        try:
            from .client_bot import Client as Bot_Client
        except Exception:
            Bot_Client = None

        if Bot_Client:
            try:
                client = Bot_Client(self.token[:6]) if hasattr(Bot_Client, '__call__') else Bot_Client()
                # prefer username lookup when possible
                chat_info = await self.get_chat(user_id)
                username = chat_info.get('data', {}).get('chat', {}).get('username')
                if username:
                    members = client.get_all_members(chat_id, search_text=username)
                    return any(m.get('username') == username for m in members)
                user_guid = chat_info.get('data', {}).get('chat', {}).get('user_id')
                if user_guid:
                    guids = client.get_all_members(chat_id, just_get_guids=True)
                    return user_guid in guids
            except Exception:
                return False

        # fallback
        logger.warning(f"check_join called for chat_id: {chat_id}, user_id: {user_id}. BotClient not available, returning False.")
        return False

    # New method: get_all_member (placeholder for rubka)
    async def get_all_member(self, chat_id: str) -> List[Dict[str, Any]]:
        """Attempt to return members using BotClient Client if available.

        Returns empty list when not available.
        """
        try:
            from .client_bot import Client as Bot_Client
        except Exception:
            Bot_Client = None

        if Bot_Client:
            try:
                client = Bot_Client(self.token[:6]) if hasattr(Bot_Client, '__call__') else Bot_Client()
                return client.get_all_members(chat_id)
            except Exception:
                return []

        logger.warning(f"get_all_member called for chat_id: {chat_id}. BotClient not available, returning empty list.")
        return []

    async def get_updates(self, offset_id: Optional[str] = None, limit: Optional[int] = None, timeout: int = 20) -> Dict[str, Any]:
        """High-performance update polling."""
        data = {
            "offset_id": offset_id,
            "limit": limit or 100  # Get more updates at once
        }
        # Clean dict
        data = {k: v for k, v in data.items() if v is not None}
        # Use a small retry loop for transient network/timeouts. Long polling
        # timeouts are expected; we convert them to an empty updates response
        # rather than bubbling an exception which stops the loop.
        attempts = 3
        backoff = 0.1
        for attempt in range(attempts):
            try:
                return await self._post("getUpdates", data, timeout=timeout)
            except Exception as e:
                # Unwrap cause for timeout detection
                cause = getattr(e, '__cause__', None)
                msg = str(e).lower()
                is_timeout = isinstance(e, asyncio.TimeoutError) or isinstance(cause, asyncio.TimeoutError) or ('timed out' in msg) or ('timeout' in msg)
                # For timeouts, return empty updates so the polling loop continues
                if is_timeout:
                    logger.warning(f"getUpdates timed out (attempt {attempt+1}/{attempts}), returning empty update list")
                    return {"status": "OK", "data": {"updates": []}}

                # For other transient network errors, retry a couple times
                if isinstance(e, APIRequestError) or isinstance(e, aiohttp.ClientError):
                    if attempt < attempts - 1:
                        await asyncio.sleep(backoff * (2 ** attempt))
                        continue
                    logger.error(f"getUpdates failed after {attempts} attempts: {e}")
                    # Convert to empty list rather than raise to keep bot running
                    return {"status": "OK", "data": {"updates": []}}

                # Otherwise, re-raise unknown errors
                raise

    async def forward_message(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False) -> Dict[str, Any]:
        return await self._post("forwardMessage", {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification})

    async def edit_message_text(self, chat_id: str, message_id: str, text: str) -> Dict[str, Any]:
        return await self._post("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def edit_inline_keypad(self,chat_id: str,message_id: str,inline_keypad: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("editMessageKeypad", {"chat_id": chat_id,"message_id": message_id, "inline_keypad": inline_keypad})

    async def delete_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        return await self._post("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def set_commands(self, bot_commands: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self._post("setCommands", {"bot_commands": bot_commands})

    async def update_bot_endpoint(self, url: str, type: str) -> Dict[str, Any]:
        return await self._post("updateBotEndpoints", {"url": url, "type": type})

    async def remove_keypad(self, chat_id: str) -> Dict[str, Any]:
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Removed"})

    async def edit_chat_keypad(self, chat_id: str, chat_keypad: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad})

    # Additional API methods from rubpy for enhanced functionality
    async def get_chat_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Get information about a member of a chat."""
        return await self._post("getChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def pin_chat_message(self, chat_id: str, message_id: str, disable_notification: bool = False) -> Dict[str, Any]:
        """Pin a message in a chat."""
        return await self._post("pinChatMessage", {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        })

    async def unpin_chat_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        """Unpin a message in a chat."""
        return await self._post("unpinChatMessage", {
            "chat_id": chat_id,
            "message_id": message_id
        })

    async def unpin_all_chat_messages(self, chat_id: str) -> Dict[str, Any]:
        """Unpin all messages in a chat."""
        return await self._post("unpinAllChatMessages", {"chat_id": chat_id})

    async def get_chat_administrators(self, chat_id: str) -> Dict[str, Any]:
        """Get a list of administrators in a chat."""
        return await self._post("getChatAdministrators", {"chat_id": chat_id})

    async def get_chat_member_count(self, chat_id: str) -> Dict[str, Any]:
        """Get the number of members in a chat."""
        return await self._post("getChatMemberCount", {"chat_id": chat_id})

    async def ban_chat_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Ban a member from a chat."""
        return await self._post("banChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def unban_chat_member(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Unban a member from a chat."""
        return await self._post("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def send_photo(
        self,
        chat_id: str,
        photo: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        caption: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send photo (supports file path or file_id/photo string)."""
        # If photo is a path, upload it first
        if photo and isinstance(photo, (str, Path)) and Path(photo).exists():
            file_name = Path(photo).name
            upload_url = await self.get_upload_url("Image")
            file_id = await self.upload_file(upload_url, file_name, photo)
            photo = file_id
        
        # If photo is still a string (file_id from API), use it directly
        if not photo and not file_id:
            raise ValueError("Either photo (path/file_id) or file_id must be provided.")
        
        photo_id = photo or file_id
        payload = {"chat_id": chat_id, "photo": photo_id, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        return await self._post("sendPhoto", payload)

    async def send_video(
        self,
        chat_id: str,
        video: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        caption: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send video (supports file path or file_id/video string)."""
        # If video is a path, upload it first
        if video and isinstance(video, (str, Path)) and Path(video).exists():
            file_name = Path(video).name
            upload_url = await self.get_upload_url("Video")
            file_id = await self.upload_file(upload_url, file_name, video)
            video = file_id
        
        # If video is still a string (file_id from API), use it directly
        if not video and not file_id:
            raise ValueError("Either video (path/file_id) or file_id must be provided.")
        
        video_id = video or file_id
        payload = {"chat_id": chat_id, "video": video_id, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        return await self._post("sendVideo", payload)

    async def send_document(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        document: Optional[str] = None,  # Legacy support
        text: Optional[str] = None,
        caption: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send document (supports file path or file_id/document string)."""
        # Legacy support: if document is provided, use it as file_id
        if document and not file_id and not path:
            file_id = document
        
        # If path is provided, upload it first
        if path:
            file_name = Path(path).name
            upload_url = await self.get_upload_url("File")
            file_id = await self.upload_file(upload_url, file_name, path)
        
        if not file_id:
            raise ValueError("Either path, file_id, or document must be provided.")
        
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text or caption,
            "disable_notification": disable_notification,
        }
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendFile", payload)

    async def send_sticker(self, chat_id: str, sticker_id: str, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "sticker_id": sticker_id, "disable_notification": disable_notification}
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendSticker", payload)

    async def send_file(self, chat_id: str, file_id: str, **kwargs) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "file_id": file_id, **kwargs}
        return await self._post("sendFile", payload)

    # File upload/download methods (from rubpy and rubka)
    async def get_upload_url(self, media_type: Literal['File', 'Image', 'Voice', 'Music', 'Gif', 'Video']) -> str:
        """Get upload URL for file type."""
        allowed = ['File', 'Image', 'Voice', 'Music', 'Gif', 'Video']
        if media_type not in allowed:
            raise ValueError(f"Invalid media type. Must be one of {allowed}")
        result = await self._post("requestSendFile", {"type": media_type})
        return result.get("data", {}).get("upload_url")

    async def upload_file(self, upload_url: str, file_name: str, file_path: Union[str, Path]) -> str:
        """High-performance file upload implementation."""
        import mimetypes
        import os
        from io import BytesIO
        
        # Use upload semaphore to control concurrent uploads
        async with self._upload_semaphore:
            # Handle remote files efficiently
            if isinstance(file_path, str) and file_path.startswith("http"):
                # Stream directly from URL to memory for small files
                buffer = BytesIO()
                async with aiohttp.ClientSession() as dl_sess:
                    async with dl_sess.get(file_path) as resp:
                        if resp.status != 200:
                            text = await resp.text()
                            raise APIRequestError(f"Download failed ({resp.status}): {text}")
                            
                        content_length = resp.headers.get('Content-Length')
                        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
                            # Large file - use temp file to avoid memory issues
                            import tempfile
                            temp_file = tempfile.NamedTemporaryFile(delete=False)
                            temp_name = temp_file.name
                            temp_file.close()
                            
                            async with aiofiles.open(temp_name, 'wb') as af:
                                async for chunk in resp.content.iter_chunked(65536):
                                    await af.write(chunk)
                            file_path = temp_name
                            is_temp = True
                        else:
                            # Small file - keep in memory
                            async for chunk in resp.content.iter_chunked(65536):
                                buffer.write(chunk)
                            file_path = buffer
                            is_temp = False
            else:
                file_path = Path(file_path)
                is_temp = False
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        
        async with aiofiles.open(str(file_path), 'rb') as f:
            file_data = await f.read()
        
        form_data = aiohttp.FormData()
        form_data.add_field('file', file_data, filename=file_name, content_type=content_type)
        
        # Reuse bot's session when possible to improve throughput and avoid
        # creating a new ClientSession per upload.
        if hasattr(self, 'session') and self.session:
            async with self.session.post(upload_url, data=form_data) as response:
                if response.status != 200:
                    text = await response.text()
                    raise APIRequestError(f"Upload failed ({response.status}): {text}")
                data = await response.json()
                file_id = data.get('data', {}).get('file_id')
                if not file_id:
                    raise APIRequestError("No file_id in upload response")

                if is_temp:
                    os.remove(file_path)

                return file_id
        else:
            async with aiohttp.ClientSession() as upload_session:
                async with upload_session.post(upload_url, data=form_data) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise APIRequestError(f"Upload failed ({response.status}): {text}")
                    data = await response.json()
                    file_id = data.get('data', {}).get('file_id')
                    if not file_id:
                        raise APIRequestError("No file_id in upload response")

                    if is_temp:
                        os.remove(file_path)

                    return file_id

    async def get_file_url(self, file_id: str) -> str:
        """Get download URL for file_id."""
        result = await self._post("getFile", {'file_id': file_id})
        return result.get("data", {}).get("download_url")

    async def download_file(
        self,
        file_id: str,
        save_as: Optional[str] = None,
        chunk_size: int = 65536,
        as_bytes: bool = False,
        timeout: Optional[Union[int, float]] = 60.0
    ) -> Union[str, bytes]:
        """Download file by file_id."""
        import mimetypes
        
        download_url = await self.get_file_url(file_id)
        if not download_url:
            raise ValueError(f"Invalid file_id: {file_id}")

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    raise APIRequestError(f"Failed to download file: {response.status}")

                content_type = response.headers.get("Content-Type", "")
                ext = mimetypes.guess_extension(content_type) or ""
                total_size = int(response.headers.get("Content-Length", 0))

                if as_bytes:
                    content = bytearray()
                    async for chunk in response.content.iter_chunked(chunk_size):
                        content.extend(chunk)
                    return bytes(content)
                else:
                    if save_as is None:
                        save_as = f"{file_id}{ext}"

                    async with aiofiles.open(save_as, "wb") as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            await f.write(chunk)

                    return save_as

    # New send methods with file upload support (from rubka)
    async def send_image(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send image (supports file path or file_id)."""
        if path:
            file_name = Path(path).name
            upload_url = await self.get_upload_url("Image")
            file_id = await self.upload_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text,
            "disable_notification": disable_notification,
        }
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendFile", payload)

    async def send_music(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send music file."""
        if path:
            file_name = Path(path).name
            upload_url = await self.get_upload_url("Music")
            file_id = await self.upload_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text,
            "disable_notification": disable_notification,
        }
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendFile", payload)

    async def send_voice(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send voice message."""
        if path:
            file_name = Path(path).name
            upload_url = await self.get_upload_url("Voice")
            file_id = await self.upload_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text,
            "disable_notification": disable_notification,
        }
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendFile", payload)

    async def send_gif(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send GIF."""
        if path:
            file_name = Path(path).name
            upload_url = await self.get_upload_url("Gif")
            file_id = await self.upload_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text,
            "disable_notification": disable_notification,
        }
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendFile", payload)

    async def send_document(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """Send document (supports file path or file_id)."""
        if path:
            file_name = Path(path).name
            upload_url = await self.get_upload_url("File")
            file_id = await self.upload_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text,
            "disable_notification": disable_notification,
        }
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type
        
        return await self._post("sendFile", payload)

    # Context managers for better resource management
    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def stop(self):
        """Stop the bot gracefully."""
        self.running = False
        # Run shutdown handlers
        for handler in self.shutdown_handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(self)
            else:
                handler(self)
        # Wait for inflight tasks to finish (short timeout)
        if self._inflight_tasks:
            tasks = list(self._inflight_tasks.keys())
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Some inflight tasks did not finish within timeout; cancelling them.")
                for t in tasks:
                    if not t.done():
                        t.cancel()

        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("Bot stopped")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    def __enter__(self):
        """Sync context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        self.running = False