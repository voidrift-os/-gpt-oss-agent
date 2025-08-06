"""A very small stub of the aiosqlite package used for testing.

This module provides a minimal asynchronous wrapper around Python's built-in
``sqlite3`` module sufficient for SQLAlchemy's async SQLite dialect during
tests. It is **not** a complete implementation of the real ``aiosqlite``
package.
"""

from __future__ import annotations

import asyncio
import sqlite3
from typing import Any, Iterable, Optional

# Expose sqlite3 exceptions/attributes expected by SQLAlchemy
Error = sqlite3.Error
DatabaseError = sqlite3.DatabaseError
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info


class Cursor:
    def __init__(self, cursor: sqlite3.Cursor, loop: asyncio.AbstractEventLoop):
        self._cursor = cursor
        self._loop = loop

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None):
        if parameters is None:
            await self._loop.run_in_executor(None, self._cursor.execute, sql)
        else:
            await self._loop.run_in_executor(None, self._cursor.execute, sql, parameters)
        return self

    async def fetchone(self):
        return await self._loop.run_in_executor(None, self._cursor.fetchone)

    async def fetchall(self):
        return await self._loop.run_in_executor(None, self._cursor.fetchall)

    async def close(self):
        await self._loop.run_in_executor(None, self._cursor.close)

    @property
    def description(self):  # pragma: no cover - passthrough
        return self._cursor.description

    @property
    def lastrowid(self):  # pragma: no cover - passthrough
        return self._cursor.lastrowid

    @property
    def rowcount(self):  # pragma: no cover - passthrough
        return self._cursor.rowcount

    # Context manager support
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


class Connection:
    def __init__(self, conn: sqlite3.Connection, loop: asyncio.AbstractEventLoop):
        self._conn = conn
        self._loop = loop
        self.daemon = False  # compatibility attribute expected by SQLAlchemy

    async def cursor(self) -> Cursor:
        cur = await self._loop.run_in_executor(None, self._conn.cursor)
        return Cursor(cur, self._loop)

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None):
        async with await self.cursor() as cursor:
            await cursor.execute(sql, parameters)
            return cursor

    async def commit(self):
        await self._loop.run_in_executor(None, self._conn.commit)

    async def rollback(self):
        await self._loop.run_in_executor(None, self._conn.rollback)

    async def close(self):
        await self._loop.run_in_executor(None, self._conn.close)

    async def create_function(self, *args, **kwargs):
        await self._loop.run_in_executor(None, lambda: self._conn.create_function(*args, **kwargs))

    # Context manager support
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    # Thread interface compatibility
    def start(self) -> None:  # pragma: no cover - no-op for tests
        return None

    # Allow ``await connection``
    def __await__(self):  # pragma: no cover
        async def _return_self():
            return self

        return _return_self().__await__()


def connect(database: str, *args: Any, **kwargs: Any) -> Connection:
    loop = asyncio.get_event_loop()
    conn = sqlite3.connect(database, *args, **kwargs)
    return Connection(conn, loop)

