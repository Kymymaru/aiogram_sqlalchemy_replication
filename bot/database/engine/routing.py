from typing import List, Optional, AsyncContextManager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
import random


class RoutedSessionMaker:
    """Управляет маршрутизацией между ведущими и подчиненными движками для балансировки нагрузки."""

    Mode_RoundRobin = 1 << 0
    Mode_Random = 1 << 1

    def __init__(self, balancing_mode: int = Mode_RoundRobin):
        """
        Инициализирует RoutedSessionMaker.

        :param balancing_mode: Режим балансировки нагрузки (циклический или случайный).
        """
        self._mode = balancing_mode
        self._engines: List[RoutedEngine] = []
        self.last_master = 0
        self.last_slave = 0

    def add_engine(self, engine: 'RoutedEngine') -> None:
        """Добавляет новый движок в список управляемых движков."""
        self._engines.append(engine)

    def get_engines(self) -> List['RoutedEngine']:
        """Возвращает все зарегистрированные движки."""
        return self._engines

    def get_master_engines(self) -> List[AsyncEngine]:
        """Возвращает список всех мастер-движков."""
        return [e._engine for e in self._engines if e._type == RoutedEngine.Engine_Master]

    def get_session(self) -> AsyncContextManager[AsyncSession]:
        """Создает сессию, используя маршрутизированные движки."""
        selected_engine = self.get_engine(flushing=False)
        session_maker = async_sessionmaker(selected_engine, expire_on_commit=False)
        return session_maker()

    def get_engine(self, flushing: bool = False) -> Optional[AsyncEngine]:
        """
        Возвращает подходящий движок на основе режима маршрутизации и типа операции.

        :param flushing: Если True, используется мастер-движок; иначе используется подчиненный.
        :return: Выбранный движок или None, если подходящий движок не найден.
        """
        engines = [e._engine for e in self._engines if
                   e._type == (RoutedEngine.Engine_Master if flushing else RoutedEngine.Engine_Slave)]

        if not engines:
            raise RuntimeError("Нет подходящих движков для выполнения запрошенной операции.")

        if self._mode == self.Mode_RoundRobin:
            index = (self.last_master if flushing else self.last_slave) % len(engines)
            if flushing:
                self.last_master = (self.last_master + 1) % len(engines)
            else:
                self.last_slave = (self.last_slave + 1) % len(engines)
            return engines[index]
        elif self._mode == self.Mode_Random:
            return random.choice(engines)
        else:
            raise ValueError("Указан неверный режим балансировки.")


class RoutedEngine:
    """Представляет конфигурацию движка для маршрутизации мастера или подчиненного."""
    Engine_Slave = 1 << 0
    Engine_Master = 1 << 1

    def __init__(self, engine_type: int = Engine_Slave, engine: Optional[AsyncEngine] = None):
        """
        Инициализирует RoutedEngine.

        :param engine_type: Тип движка (мастер или подчиненный).
        :param engine: Экземпляр движка SQLAlchemy.
        """
        self._type = engine_type
        self._engine = engine

    def __repr__(self) -> str:
        """Возвращает строковое представление типа движка."""
        engine_type = "Master" if self._type == self.Engine_Master else "Slave"
        return f"{engine_type}: {self._engine}"

    @property
    def engine(self):
        return self._engine


# Глобальный экземпляр маршрутизатора сессий
__sessionmaker = RoutedSessionMaker()


def Configure(mode: int = RoutedSessionMaker.Mode_RoundRobin, engines: Optional[List[RoutedEngine]] = None) -> None:
    """
    Конфигурирует глобальный экземпляр RoutedSessionMaker.

    :param mode: Режим балансировки нагрузки.
    :param engines: Список экземпляров RoutedEngine для инициализации.
    """
    global __sessionmaker
    __sessionmaker = RoutedSessionMaker(balancing_mode=mode)
    if engines:
        for engine in engines:
            __sessionmaker.add_engine(engine)


def api() -> RoutedSessionMaker:
    """Возвращает сконфигурированный глобальный экземпляр RoutedSessionMaker."""
    global __sessionmaker
    return __sessionmaker
