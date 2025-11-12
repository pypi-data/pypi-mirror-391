import asyncio
import time
from typing import AsyncGenerator, AsyncIterable, Generic, TypeVar

from .asyncio import run_in_threadpool
from .utils import DummyStopIteration, next_without_stop_iteration


async def to_aiterator(iterator):
    iterator = await run_in_threadpool(iter, iterator)
    while True:
        try:
            yield await run_in_threadpool(next_without_stop_iteration, iterator)
        except DummyStopIteration:
            break


async def rate_limit_iterator(aiterator, iters_per_second):
    start = time.time()
    i = 0
    async for it in aiterator:
        yield it
        await asyncio.sleep((i / iters_per_second) - (time.time() - start))
        i += 1


T = TypeVar("T")


class BaseStreamQueue(Generic[T]):
    _CLOSE = object()

    def __init__(self):
        self.queue = asyncio.Queue()

    async def close(self):
        await self.queue.put(self._CLOSE)


class StreamQueue(BaseStreamQueue):
    queue: asyncio.Queue[T]

    def put(self, data: T) -> None:
        return self.queue.put(data)

    async def __aiter__(self) -> AsyncGenerator[T]:
        while (it := await self.queue.get()) is not self._CLOSE:
            yield it


class StreamIteratorQueue(BaseStreamQueue):
    queue: asyncio.Queue[AsyncIterable[T]]

    def put(self, data: AsyncIterable[T]) -> None:
        return self.queue.put(data)

    async def __aiter__(self) -> AsyncGenerator[T]:
        while (iterator := await self.queue.get()) is not self._CLOSE:
            async for it in iterator:
                yield it
