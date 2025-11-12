import asyncio
import logging
import platform
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from .message_queue import MessageQueue
from .client_bot.network.socket import Socket
from .client_bot.network.network import Network

logger = logging.getLogger(__name__)

class AsyncSocketManager:
    def __init__(self, auth: str, app_name: str = "Main"):
        # Default event loop is used for better compatibility
        logger.info('Using default event loop')
            
        self.auth = auth
        self.app_name = app_name
        self.socket = Socket(self.auth, app_name=app_name)
        self.network = Network(self.auth)
        self.message_queue = MessageQueue(maxsize=50000)
        self.running = False
        self.thread_pool = ThreadPoolExecutor(max_workers=4)  # For CPU intensive tasks
        self.poll_interval = 0.01  # Start with aggressive polling
        self.backoff_factor = 1.5
        self.max_poll_interval = 1.0  # Max 1 second between polls
        self._last_seq = 0
        self._message_handlers = []
        
    def add_message_handler(self, handler):
        """Add a message handler function."""
        self._message_handlers.append(handler)
        
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a single message through all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                
    async def _socket_handler(self) -> None:
        """Handle socket connection and message receiving."""
        while self.running:
            try:
                if not self.socket.connected:
                    await asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        self.socket.connect
                    )
                
                updates = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    self.socket.get_updates
                )
                
                if updates:
                    # Reset poll interval on successful updates
                    self.poll_interval = 0.01
                    
                    for update in updates:
                        if self._is_new_message(update):
                            await self.message_queue.put(update)
                else:
                    # Back off polling rate when no updates
                    self.poll_interval = min(
                        self.poll_interval * self.backoff_factor,
                        self.max_poll_interval
                    )
                
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Socket handler error: {e}")
                self.socket.disconnect()
                await asyncio.sleep(1)
                
    def _is_new_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is new based on sequence number."""
        seq = message.get("seq", 0)
        if seq > self._last_seq:
            self._last_seq = seq
            return True
        return False
                
    async def start(self, num_processors: int = 10) -> None:
        """Start the socket manager and message processors."""
        self.running = True
        self.message_queue.start(self._process_message, num_processors)
        asyncio.create_task(self._socket_handler())
        
    async def stop(self) -> None:
        """Stop the socket manager and cleanup resources."""
        self.running = False
        await self.message_queue.stop()
        self.socket.disconnect()
        self.thread_pool.shutdown(wait=False)