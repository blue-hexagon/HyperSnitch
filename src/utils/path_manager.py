from pathlib import Path

from src.utils.singleton import Singleton


class PathManager(metaclass=Singleton):
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.src_root = Path(__file__).parent.parent
        print(self.root)
        print(self.src_root)


