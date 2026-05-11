import logging

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger import ExternalLogger

class MambaExternalLogger(ExternalLogger):
    def __new__(cls, name: str):
        # Bypass the base class __new__ restriction
        instance = object.__new__(cls)
        return instance

    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.logger = logging.getLogger(name)

    @staticmethod
    def get_logger(name: str):
        return MambaExternalLogger(name)
    
    def performance(self, message: str) -> None:
        self.logger.debug(f"[{self.name}] {message}")

    def information(self, message: str) -> None:
        pass
        # self.logger.info(f"[{self.name}] {message}")

    def warning(self, message: str) -> None:
        self.logger.warning(f"[{self.name}] {message}")
    
    def error(self, message: str) -> None:
        self.logger.error(f"[{self.name}] {message}")

    def fatal(self, message: str) -> None:
        self.logger.critical(f"[{self.name}] {message}")    