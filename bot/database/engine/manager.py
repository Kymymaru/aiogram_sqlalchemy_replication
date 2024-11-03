from contextlib import asynccontextmanager
from typing import AsyncIterator, AsyncContextManager, overload

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from bot.database.engine.routing import RoutedSessionMaker, RoutedEngine, Configure
from config import DatabaseConfig
from bot.database.models import Base


class DbManager:
    def __init__(self):
        self.routed_session_maker: RoutedSessionMaker | None = None

    def initialize(self, config: DatabaseConfig, mode: int = RoutedSessionMaker.Mode_RoundRobin):
        """Инициализация DbManager с мастером и подчиненными движками на основе конфигурации."""
        self.routed_session_maker = RoutedSessionMaker(balancing_mode=mode)

        # Создание движка для мастера
        master_engine = create_async_engine(
            url=f'mysql+aiomysql://{config.master.user}:{config.master.password}@{config.master.host}/{config.master.database}'
        )
        self.routed_session_maker.add_engine(RoutedEngine(engine_type=RoutedEngine.Engine_Master, engine=master_engine))

        # Создание движков для подчиненных
        for slave_config in config.slaves:
            slave_engine = create_async_engine(
                url=f'mysql+aiomysql://{slave_config.user}:{slave_config.password}@{slave_config.host}/{slave_config.database}'
            )
            self.routed_session_maker.add_engine(
                RoutedEngine(engine_type=RoutedEngine.Engine_Slave, engine=slave_engine))

        # Конфигурирование глобального маршрутизатора сессий
        Configure(mode=mode, engines=self.routed_session_maker.get_engines())

    @overload
    def get_session(self) -> AsyncContextManager[AsyncSession]:
        ...

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Создает и возвращает асинхронную сессию с поддержкой маршрутизации."""
        if self.routed_session_maker is None:
            raise RuntimeError("Менеджер базы данных не инициализирован. Сначала вызовите метод initialize().")
        async with self.routed_session_maker.get_session() as session:
            try:
                yield session
            finally:
                await session.close()

    async def create_tables(self, debug: bool = False) -> None:
        """Создает таблицы во всех мастер-движках."""
        if self.routed_session_maker is None:
            raise RuntimeError("Менеджер базы данных не инициализирован. Сначала вызовите метод initialize().")

        master_engines = self.routed_session_maker.get_master_engines()
        for engine in master_engines:
            async with engine.begin() as conn:
                if debug:
                    await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

    async def dispose(self):
        """Закрывает все движки базы данных."""
        if self.routed_session_maker is not None:
            for engine in self.routed_session_maker.get_engines():
                await engine.engine.dispose()
