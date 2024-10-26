from typing import Any


class Singleton(type):
    """ Usage: class ClassName(metaclass=Singleton) """

    _instances = {}

    def __call__(cls, *args, **kwargs) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
