# price_monitoring/parsers/csmoney/csmoney_parser.py
import asyncio
import logging

from .parser import AbstractCsmoneyParser, MaxAttemptsReachedError
from .task_scheduler import RedisTaskScheduler, RenewFailedError
from ..abstract_parser import AbstractParser
from ...decorators import async_infinite_loop
from ...models.csmoney import CsmoneyTask
from ...queues import AbstractCsmoneyWriter

logger = logging.getLogger(__name__)

_TASK_LOCK_RENEW_INTERVAL = 10


class CsmoneyParser(AbstractParser):
    def __init__(
        self,
        impl: AbstractCsmoneyParser,
        result_queue: AbstractCsmoneyWriter,
        task_scheduler: RedisTaskScheduler,
    ):
        self._impl = impl
        self._result_queue = result_queue
        self._task_scheduler = task_scheduler

    async def run(self) -> None:
        await self._run_csmoney_parser()

    @async_infinite_loop(logger)
    async def _run_csmoney_parser(self) -> None:
        task = await self._task_scheduler.get_task()
        if not task:
            await asyncio.sleep(0.5)
            return

        is_success = False
        lock_renew_task = None
        try:
            lock_renew_task = asyncio.create_task(self._renew_lock(task))
            await self._impl.parse(
                url=task.url, result_queue=self._result_queue, max_attempts=300
            )
            is_success = True
        except MaxAttemptsReachedError:
            logger.warning(f"Failed to parse {task.url}. Too many attempts!")
        except Exception as exc:
            logger.exception(exc)
        finally:
            if lock_renew_task:
                lock_renew_task.cancel()
        await self._task_scheduler.release_task(task, is_success)

    async def _renew_lock(self, task: CsmoneyTask) -> None:
        while True:
            await asyncio.sleep(_TASK_LOCK_RENEW_INTERVAL)
            try:
                await self._task_scheduler.renew_task_lock(task)
                logger.info("Lock for task successfully renewed")
            except RenewFailedError:
                logger.warning("Lock for task renew has failed!")
                break