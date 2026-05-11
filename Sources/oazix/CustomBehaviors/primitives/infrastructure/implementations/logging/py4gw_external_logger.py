from enum import Enum

import Py4GW
from Sources.oazix.CustomBehaviors.primitives.infrastructure.contracts.logging.external_logger import ExternalLogger


class LoggerLevel(Enum):
        Performance = 0
        Information = 1
        Warning = 2
        Error = 3
        Fatal = 4

class Py4gwExternalLogger(ExternalLogger):
    def __new__(cls, name: str):
        # Bypass the base class __new__ restriction
        instance = object.__new__(cls)
        return instance

    def __init__(self, name: str):
        self.name = name
        self.is_active = True

    @staticmethod
    def get_logger(name: str):
        return Py4gwExternalLogger(name)

    def __log(self, message: str, level: LoggerLevel = LoggerLevel.Information) -> None:
        if not self.is_active:
            return

        # Map LoggerLevel to Py4GW.Console.MessageType
        message_type_map = {
            LoggerLevel.Performance: Py4GW.Console.MessageType.Performance,
            LoggerLevel.Information: Py4GW.Console.MessageType.Info,
            LoggerLevel.Warning: Py4GW.Console.MessageType.Warning,
            LoggerLevel.Error: Py4GW.Console.MessageType.Error,
            LoggerLevel.Fatal: Py4GW.Console.MessageType.Error,  # Fatal maps to Error since Py4GW doesn't have Fatal
        }

        msg_type = message_type_map.get(level, Py4GW.Console.MessageType.Info)
        Py4GW.Console.Log(self.name, message, msg_type)

    def performance(self, message: str) -> None:
        self.__log(message, LoggerLevel.Performance)

    def information(self, message: str) -> None:
        pass
        # self.__log(message, LoggerLevel.Information)

    def warning(self, message: str) -> None:
        self.__log(message, LoggerLevel.Warning)

    def error(self, message: str) -> None:
        self.__log(message, LoggerLevel.Error)

    def fatal(self, message: str) -> None:
        self.__log(message, LoggerLevel.Fatal)