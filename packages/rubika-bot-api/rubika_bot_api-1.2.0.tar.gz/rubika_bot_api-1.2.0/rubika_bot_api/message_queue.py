import asyncio
import logging
from typing import Any, Dict, List, Optional
from collections import deque

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self, maxsize: int = 10000):
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.processors: List[asyncio.Task] = []
        self.processor_semaphore = asyncio.Semaphore(500)
        self.processed_messages = deque(maxlen=10000)
        self.is_running = False
    
    def start(self, process_func, num_processors: int = 10):
        """Start message processors."""
        self.is_running = True
        self.processors = [
            asyncio.create_task(self._processor(process_func))
            for _ in range(num_processors)
        ]
    
    async def put(self, message: Dict[str, Any]) -> None:
        """Queue a message for processing."""
        try:
            await self.queue.put(message)
        except asyncio.QueueFull:
            # If queue is full, still try to process but log warning
            logger.warning("Message queue full - may cause backpressure")
            await self.queue.put(message)
    
    async def _processor(self, process_func) -> None:
        """Process messages from the queue."""
        while self.is_running:
            try:
                message = await self.queue.get()
                try:
                    # Use semaphore to control concurrent processing
                    async with self.processor_semaphore:
                        await process_func(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processor error: {e}")
                await asyncio.sleep(0.1)
    
    def is_full(self) -> bool:
        """Check if queue is near capacity."""
        return self.queue.qsize() > self.queue.maxsize * 0.9
    
    async def stop(self) -> None:
        """Stop all processors and wait for queue to empty."""
        self.is_running = False
        for processor in self.processors:
            processor.cancel()
        
        if not self.queue.empty():
            try:
                await asyncio.wait_for(self.queue.join(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Queue did not empty during shutdown")
        
        # Wait for all processors to finish
        await asyncio.gather(*self.processors, return_exceptions=True)