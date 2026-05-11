from abc import abstractmethod

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger import ExternalLogger

class ExternalLoggerFactory:

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExternalLoggerFactory, cls).__new__(cls)
        return cls._instance

    @abstractmethod
    def get_logger(self, name: str) -> ExternalLogger:
        raise NotImplementedError("get_logger method not implemented")