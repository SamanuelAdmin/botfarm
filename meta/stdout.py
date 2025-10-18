from abc import ABC, abstractmethod


class IStdout(ABC):
    @abstractmethod
    def write(self, text: str) -> None: ...
    @abstractmethod
    def flush(self) -> None: ...