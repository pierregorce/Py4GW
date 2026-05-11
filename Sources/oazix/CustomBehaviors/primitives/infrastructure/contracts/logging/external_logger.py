from abc import abstractmethod

class ExternalLogger:
        
    def __new__(cls):
        raise TypeError("Cannot instantiate directly. Use get_logger() method.")

    @abstractmethod
    def performance(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def information(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def fatal(self, message: str) -> None:
        raise NotImplementedError