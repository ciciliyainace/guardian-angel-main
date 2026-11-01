import asyncio
from typing import Dict, Any
from app.core.database import SessionLocal
from app.services.event_service import EventService
from app.core.logging_config import logger


class DetectionWorker:
    def __init__(self, max_queue_size: int = 1000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.is_running = False
        self._task = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._consume())
        logger.info("DetectionWorker queue consumer started.")

    def stop(self):
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("DetectionWorker queue consumer stopped.")

    async def enqueue(self, event_data: Dict[str, Any]):
        try:
            self.queue.put_nowait(event_data)
        except asyncio.QueueFull:
            logger.warning("DetectionWorker queue is full, dropping event to prevent memory exhaustion.")

    async def _consume(self):
        while self.is_running:
            try:
                event_data = await self.queue.get()
                db = SessionLocal()
                try:
                    svc = EventService(db)
                    svc.ingest_event(event_data, run_detection=True)
                finally:
                    db.close()
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DetectionWorker consumption: {e}")


detection_worker = DetectionWorker()
