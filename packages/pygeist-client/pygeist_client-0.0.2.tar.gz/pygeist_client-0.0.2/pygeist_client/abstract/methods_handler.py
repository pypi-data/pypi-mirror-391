from typing import Any
from pygeist_client._adapter import METHODS
from abc import ABC, abstractmethod


class AsyncMethodHandler(ABC):
    @abstractmethod
    async def _handle(self, method: int, *ag, **kw) -> Any:
        pass

    async def post(self, *ag, **kw):
        return await self._handle(METHODS['POST'], *ag, **kw)

    async def get(self, *ag, **kw):
        return await self._handle(METHODS['GET'], *ag, **kw)

    async def put(self, *ag, **kw):
        return await self._handle(METHODS['PUT'], *ag, **kw)

    async def delete(self, *ag, **kw):
        return await self._handle(METHODS['DELETE'], *ag, **kw)

    async def head(self, *ag, **kw):
        return await self._handle(METHODS['HEAD'], *ag, **kw)

    async def connect(self, *ag, **kw):
        return await self._handle(METHODS['connect'], *ag, **kw)

    async def options(self, *ag, **kw):
        return await self._handle(METHODS['OPTIONS'], *ag, **kw)

    async def trace(self, *ag, **kw):
        return await self._handle(METHODS['TRACE'], *ag, **kw)

    async def patch(self, *ag, **kw):
        return await self._handle(METHODS['PATCH'], *ag, **kw)
