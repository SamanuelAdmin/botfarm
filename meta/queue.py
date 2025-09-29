from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class IQueue(ABC):
    @abstractmethod
    def add(self, obj: Any) -> None: ...
    @abstractmethod
    def get(self) -> Any: ...

    @abstractproperty
    def size(self) -> int: ...