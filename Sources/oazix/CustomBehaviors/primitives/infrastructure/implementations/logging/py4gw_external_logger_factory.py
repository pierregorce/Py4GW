from enum import Enum

from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger import ExternalLogger
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger_factory import ExternalLoggerFactory
from Sources.oazix.CustomBehaviors.primitives.infrastructure.implementations.logging.py4gw_external_logger import Py4gwExternalLogger

class Py4gwExternalLoggerFactory(ExternalLoggerFactory):
    
    def __new__(cls):
        # Bypass the base class __new__ restriction
        instance = object.__new__(cls)
        return instance

    def get_logger(self, name: str) -> ExternalLogger:
        return Py4gwExternalLogger.get_logger(name)