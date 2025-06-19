import importlib.util
import os
import types
import sys

class WidgetHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

def main():
    pass

# This ensures that Main() is called when the script is executed directly.
if __name__ == "__main__":
    main()