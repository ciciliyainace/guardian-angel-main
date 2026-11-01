import asyncio
from app.core.database import SessionLocal
from app.services.event_service import EventService
from app.collectors import JsonFileCollector, SuricataCollector, WindowsCollector
from app.core.logging_config import logger


class IngestionWorker:
    def __init__(self, poll_interval_sec: int = 15):
        self.poll_interval = poll_interval_sec
        self.is_running = False
        self._task = None
        self.collectors = [
            JsonFileCollector(),
            SuricataCollector(),
            WindowsCollector(),
        ]

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        for c in self.collectors:
            c.start()
        self._task = asyncio.create_task(self._run_loop())
        logger.info("IngestionWorker background task started.")

    def stop(self):
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        for c in self.collectors:
            c.stop()
        logger.info("IngestionWorker background task stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                from app.core.database import db_manager
                if not db_manager.is_connected:
                    await asyncio.sleep(self.poll_interval)
                    continue

                for col in self.collectors:
                    try:
                        new_records = col.collect()
                        if new_records:
                            db = SessionLocal()
                            try:
                                svc = EventService(db)
                                for rec in new_records:
                                    svc.ingest_event(rec, run_detection=True)
                            finally:
                                db.close()
                    except Exception as e:
                        logger.error(f"Error collecting from {col.name}: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in IngestionWorker: {e}")

            await asyncio.sleep(self.poll_interval)


ingestion_worker = IngestionWorker()
