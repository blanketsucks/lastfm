from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, List, Coroutine, TypeVar, Generator, Optional
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from typing_extensions import Self

T = TypeVar('T')

__all__ = (
    'Paginator',
)

class EmptyPage(Exception):
    pass

class MaxReached(Exception):
    pass

class AbstractPaginator(ABC, Generic[T]):
    items: List[T]

    @abstractmethod
    async def next(self) -> List[T]:
        raise NotImplementedError

    async def all(self) -> List[T]:
        return [item async for item in self]

    def __await__(self) -> Generator[None, None, List[T]]:
        return self.all().__await__()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> T:
        try:
            if self.items:
                return self.items.pop()

            await self.next()
            return self.items.pop()
        except (EmptyPage, MaxReached):
            raise StopAsyncIteration


class Paginator(AbstractPaginator[T]):
    MAX_PAGES = 1000

    __slots__ = (
        'items', 
        'page', 
        'limit',
        'max',
        'offset',
        'callback',
        'args', 
        'kwargs'
    )

    def __init__(
        self,
        callback: Callable[..., Coroutine[None, None, List[T]]],
        *args: Any,
        limit: int = 30,
        max: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        self.items: List[T] = []
        self.page = 1
        self.offset = 0
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

        if max:
            if max < 0:
                raise ValueError('max must be greater than 0')

            self.limit = min(limit, max)
        else:
            self.limit = limit
    
        self.max = max

    def __repr__(self):
        return f'<Paginator page={self.page} limit={self.limit}>'

    def __len__(self):
        return len(self.items)

    async def next(self) -> List[T]:
        if self.max is not None and self.offset >= self.max:
            raise MaxReached
        elif self.page > self.MAX_PAGES:
            raise MaxReached

        items = await self.callback(
            *self.args, 
            page=self.page, 
            limit=self.limit, 
            **self.kwargs
        )

        if not items:
            raise EmptyPage

        self.page += 1
        self.offset += len(items)

        self.items.extend(items)
        return items
