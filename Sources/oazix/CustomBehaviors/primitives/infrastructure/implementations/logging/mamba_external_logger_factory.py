from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger import ExternalLogger
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger_factory import ExternalLoggerFactory
from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.logging.mamba_external_logger import MambaExternalLogger

class MambaExternalLoggerFactory(ExternalLoggerFactory):
    
    def __new__(cls):
        # Bypass the base class __new__ restriction
        instance = object.__new__(cls)
        return instance

    def get_logger(self, name: str) -> ExternalLogger:
        return MambaExternalLogger.get_logger(name)