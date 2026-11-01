import asyncio
from app.core.database import SessionLocal, db_manager
from app.services.firewall_service import FirewallService
from app.core.logging_config import logger


class FirewallExpiryWorker:
    def __init__(self, check_interval_sec: int = 30):
        self.check_interval = check_interval_sec
        self.is_running = False
        self._task = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("FirewallExpiryWorker background task started.")

    def stop(self):
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("FirewallExpiryWorker background task stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                if not db_manager.is_connected:
                    await asyncio.sleep(self.check_interval)
                    continue
                db = SessionLocal()
                try:
                    svc = FirewallService(db)
                    expired_count = svc.process_expired_rules()
                    if expired_count > 0:
                        logger.info(f"FirewallExpiryWorker cleaned up {expired_count} expired firewall rules.")
                finally:
                    db.close()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in FirewallExpiryWorker loop: {e}")

            await asyncio.sleep(self.check_interval)


expiry_worker = FirewallExpiryWorker()
