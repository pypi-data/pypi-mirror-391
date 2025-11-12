from .pkginstaller import PackageInstaller as PackageInstaller
from typing import Final

class PyInstaller:
    __FOLDER: Final[str]
    @classmethod
    def generate_hook(cls, _name: str, _path: str, _hidden_imports: list[str]) -> None: ...
    @staticmethod
    def pack(spec_path: str) -> None: ...
