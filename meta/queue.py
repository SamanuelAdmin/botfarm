from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class IQueue(ABC):
    @abstractmethod
    def add(self, obj: Any) -> None: ...
    @abstractmethod
    def get(self) -> Any: ...

    @property
    @abstractmethod
    def size(self) -> int: ...