from enum import Enum

from Sources.oazix.CustomBehaviors.primitives import constants

class LoggerLevel(Enum):
        Performance = 0
        Information = 1
        Warning = 2
        Error = 3
        Fatal = 4        

class SimpleLogger:
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def get_logger(name: str):
        return SimpleLogger(name)
    
    def __log(self, message: str, level: LoggerLevel = LoggerLevel.Information) -> None:
        if constants.DEBUG: print(f"[{self.name}] {message}")

    def performance(self, message: str) -> None:
        self.__log(message, LoggerLevel.Performance)

    def information(self, message: str) -> None:
        self.__log(message, LoggerLevel.Information)

    def warning(self, message: str) -> None:
        self.__log(message, LoggerLevel.Warning)
        
    def error(self, message: str) -> None:
        self.__log(message, LoggerLevel.Error)

    def fatal(self, message: str) -> None:
        self.__log(message, LoggerLevel.Fatal)