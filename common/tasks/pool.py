from __future__ import annotations

import asyncio
import inspect
import os
import sys
import threading
import time
from collections.abc import Callable, Coroutine
from typing import Any

import celery.concurrency.base as base
import celery.signals
from billiard.einfo import ExceptionInfo
from billiard.exceptions import WorkerLostError
from celery.exceptions import WorkerShutdown, WorkerTerminate, reraise
from starlette.concurrency import run_in_threadpool

__all__ = ("AsyncIOPool",)

AnyCallable = Callable[..., Any]
AnyCoroutine = Coroutine[Any, Any, Any]
AnyException = Exception | type[Exception]
WorkerPoolInfo = dict[str, int | bool | tuple[int, ...] | str | None]


class AsyncIOPool(base.BasePool):
    """
    AsyncIO Celery Worker Pool

    特点:
    - 单独 event loop thread
    - async task 原生执行
    - sync task 自动线程池执行
    - threading.Semaphore 控制 celery backpressure
    - graceful shutdown
    - cooperative cancel
    """

    loop: asyncio.AbstractEventLoop | None
    loop_runner: threading.Thread | None
    singleton: AsyncIOPool | None = None
    _run_timeout = 300  # 外部同步调用等待结果的秒数，超时后请求取消底层协程。
    _shutdown_timeout = 60  # 正常停机时等待任务完成的秒数。
    _cancel_timeout = 5  # 停机取消任务后，等待协程执行清理的最长秒数。

    def __new__(cls, *args: Any, **kwargs: Any) -> AsyncIOPool:
        if not isinstance(cls.singleton, cls):
            from common.tasks.tracer import patch_celery_tracer

            assert patch_celery_tracer()

            cls.singleton = super().__new__(cls)

        return cls.singleton

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if getattr(self, "_initialized", False):
            return

        kwargs.update(
            threads=False,
            forking_enable=False,
        )

        super().__init__(*args, **kwargs)

        self.loop = None
        self.loop_runner = None

        # celery worker backpressure
        self._slots = threading.Semaphore(self.limit)

        # 追踪 Celery 执行入口和 run_in_pool 提交的协程，仅在事件循环线程内修改。
        self._tasks: set[asyncio.Task] = set()

        self._started = False
        self._initialized = True

    def on_start(self) -> None:
        if self._started:
            return

        self.loop = asyncio.new_event_loop()

        def runner():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.loop_runner = threading.Thread(
            target=runner,
            name="celery-aio-loop",
            daemon=False,
        )

        self.loop_runner.start()

        self._started = True

        celery.signals.worker_process_init.send(sender=None)

    def on_stop(self) -> None:
        """正常停机先等待任务完成，再取消超时任务并清理事件循环。"""
        self._stop(self._shutdown_timeout)

    def on_terminate(self) -> None:
        """强制停机立即取消任务，仍留出协程清理资源的时间。"""
        self._stop(0, close_resources=False)

    async def _drain_tasks(self, wait_timeout: float) -> None:
        """等待已追踪任务完成，超时后取消；取消清理最多等待指定时长。"""
        tasks = [task for task in self._tasks if not task.done()]
        if not tasks:
            return

        _, pending = await asyncio.wait(tasks, timeout=wait_timeout)
        for task in pending:
            task.cancel()
        if pending:
            _, pending = await asyncio.wait(pending, timeout=self._cancel_timeout)
            if pending:
                print(f"{len(pending)} tasks did not finish cancellation")

    def _stop(self, wait_timeout: float, *, close_resources: bool = True) -> None:
        """停止循环前处理任务取消，正常停机发送资源清理信号，最后关闭循环。"""
        print("Stopping AsyncIOPool...")

        if not self.loop or not self.loop.is_running():
            return

        async def shutdown():
            await self._drain_tasks(wait_timeout)
            await self.loop.shutdown_asyncgens()

        future = asyncio.run_coroutine_threadsafe(
            shutdown(),
            self.loop,
        )

        try:
            future.result(timeout=wait_timeout + self._cancel_timeout + 5)
        except Exception as e:
            future.cancel()
            print(f"shutdown error: {e}")

        if close_resources:
            celery.signals.worker_process_shutdown.send(sender=None)
        self.loop.call_soon_threadsafe(self.loop.stop)

        if self.loop_runner:
            self.loop_runner.join(timeout=5)

        if not self.loop.is_running():
            self.loop.close()
            self._started = False

        print("AsyncIOPool stopped")

    def on_apply(
        self,
        target: AnyCallable | AnyCoroutine,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        callback: Callable[[Any], None] | None = None,
        accept_callback: Callable[[Any], None] | None = None,
        pid: int | None = None,
        getpid: Callable[[], int] = os.getpid,
        propagate: tuple[AnyException, ...] = (),
        monotonic: Callable[[], int] = time.monotonic,
        **_,
    ) -> None:
        """
        celery 任务执行入口

        注意:
        这里必须阻塞 acquire

        否则:
        - worker 会疯狂从 broker reserve task
        - task 堆积在 worker memory
        - worker crash 会丢失大量任务
        """
        self.on_start()

        if self.loop is None:
            raise RuntimeError("event loop not initialized")

        kwargs = kwargs or {}

        # limit 满后阻塞 consumer
        self._slots.acquire()

        # worker accepted
        if accept_callback:
            accept_callback(pid or getpid(), monotonic())

        self.loop.call_soon_threadsafe(
            self._submit_task,
            target,
            args,
            kwargs,
            callback,
            propagate,
        )

    def _submit_task(
        self,
        target: AnyCallable | AnyCoroutine,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        callback: Callable[[Any], None] | None,
        propagate: tuple[AnyException, ...],
    ) -> None:
        """
        仅可以在事件循环线程执行
        """

        if self.loop is None:
            return

        task = self.loop.create_task(
            self._task_runner(
                target=target,
                args=args,
                kwargs=kwargs,
                callback=callback,
                propagate=propagate,
            )
        )

        self._tasks.add(task)

        def cleanup(t: asyncio.Task):
            try:
                t.result()
            except asyncio.CancelledError:
                pass
            finally:
                self._tasks.discard(t)
                self._slots.release()

        task.add_done_callback(cleanup)

    async def _task_runner(
        self,
        target: AnyCallable | AnyCoroutine,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        callback: Callable[[Any], None] | None,
        propagate: tuple[AnyException, ...],
    ) -> Any:
        """
        执行任务
        """
        try:
            # async task
            if inspect.iscoroutinefunction(target):
                result = await target(*args, **kwargs)
            # sync task
            else:
                result = await run_in_threadpool(
                    target,
                    *args,
                    **kwargs,
                )
        except propagate:
            raise
        except Exception:
            raise
        except (WorkerShutdown, WorkerTerminate):
            raise
        except BaseException as exc:
            try:
                reraise(WorkerLostError, WorkerLostError(repr(exc)), sys.exc_info()[2])
            except WorkerLostError:
                callback(ExceptionInfo())
        else:
            callback(result)

    def _get_info(self) -> WorkerPoolInfo:
        info = super()._get_info()

        tasks = self._tasks.copy()
        running_tasks = sum(not task.done() for task in tasks)

        info.update(
            max_concurrency=self.limit,
            running_tasks=running_tasks,
            total_tasks=len(tasks),
            event_loop_running=(self.loop.is_running() if self.loop else False),
            pool_type="asyncio",
        )

        return info

    async def _run_in_pool(
        self,
        task_function: AnyCallable | AnyCoroutine,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        """追踪外部提交的任务，完成、异常或取消后移除引用；不占用 Celery 接收任务的并发槽。"""
        task = asyncio.current_task()
        self._tasks.add(task)
        try:
            if inspect.iscoroutine(task_function):
                return await task_function
            if inspect.iscoroutinefunction(task_function):
                return await task_function(*args, **kwargs)
            return await run_in_threadpool(task_function, *args, **kwargs)
        finally:
            self._tasks.discard(task)

    @classmethod
    def run_in_pool(
        cls,
        task_function: AnyCallable | AnyCoroutine,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """从同步线程执行任务，等待超时后取消底层协程，避免后台任务持续积累。"""
        if not (worker_pool := cls.singleton):
            worker_pool = cls()
        worker_pool.on_start()

        result = asyncio.run_coroutine_threadsafe(
            worker_pool._run_in_pool(task_function, args, kwargs),
            worker_pool.loop,
        )
        try:
            return result.result(timeout=worker_pool._run_timeout)
        except TimeoutError:
            result.cancel()
            raise
