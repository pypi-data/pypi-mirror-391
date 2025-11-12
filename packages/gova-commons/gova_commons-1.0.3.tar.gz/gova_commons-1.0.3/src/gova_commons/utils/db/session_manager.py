from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker


class SessionManager:
    _smaker: sessionmaker[Session] = None
    _smaker_sync: sessionmaker[AsyncSession] = None

    @classmethod
    def set_smakers(
        cls,
        smaker: sessionmaker[Session] | None = None,
        smaker_sync: sessionmaker[AsyncSession] | None = None,
    ) -> None:
        if smaker is not None and cls._smaker is not None:
            cls._smaker = smaker
        if smaker_sync is not None and cls._smaker_sync is not None:
            cls._smaker_sync = smaker_sync

    @classmethod
    @asynccontextmanager
    async def get_db_sess(cls) -> AsyncGenerator[AsyncSession, None]:
        if cls._smaker is None:
            raise ValueError("Session maker not set.")

        async with cls._smaker.begin() as s:
            try:
                yield s
            except:
                await s.rollback()
                raise

    @classmethod
    @contextmanager
    def get_db_sess_sync(cls) -> Generator[Session, None, None]:
        if cls._smaker_sync is None:
            raise ValueError("Session maker not set.")

        with cls._smaker_sync.begin() as s:
            try:
                yield s
            except:
                s.rollback()
                raise
