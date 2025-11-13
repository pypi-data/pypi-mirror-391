"""
Doc String

"""
from pathlib import Path

__all__ = ["RPD"]

class RPD:
    def __init__(self, path_str):
        self.path = self._path(path_str)
        self.dir = (
            self.path 
            if self.path.is_dir() 
            else self.path.parent
        )
         
    def _path(self, path_str):
        path = Path(path_str).resolve()
        cwd = Path.cwd().resolve()
        try:
            return path.relative_to(cwd)
        except ValueError:
            return path


