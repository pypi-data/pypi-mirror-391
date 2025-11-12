import importlib
import sys
from functools import cache
from importlib.util import find_spec
from types import ModuleType
from typing import Any, ClassVar, cast

from loguru import logger


def _make_message(mod_name: str, error: Exception) -> str:
    return f"Attempted import of dependency '{mod_name}' unsuccessful ({error.__class__}): {error}"


class LazyModule(ModuleType):
    """A proxy that imports a module lazily upon first attribute access."""

    _SAFE_ATTRS: ClassVar[set[str]] = {
        "__name__",
        "__loader__",
        "__package__",
        "__spec__",
        "__path__",
        "__file__",
        "_module",
        "_load",
    }

    def __init__(self, name: str):
        super().__init__(name)
        self._module: ModuleType | None = None

    def _load(self) -> ModuleType:
        if self._module is None:
            _name = self.__name__
            sys.modules.pop(_name, None)
            module = importlib.import_module(_name)
            sys.modules[_name] = module
            setattr(self, "_module", module)
        return cast(ModuleType, self._module)

    def __getattribute__(self, attr: str) -> Any:
        if attr in object.__getattribute__(self, "_SAFE_ATTRS"):
            return object.__getattribute__(self, attr)

        module = (
            object.__getattribute__(self, "_module") or object.__getattribute__(self, "_load")()
        )
        return getattr(module, attr)

    def __dir__(self) -> list[str]:
        self._load()
        return dir(self._module)

    def __repr__(self):
        return f"<LazyModule proxy for '{self.__name__}'>"


@cache
def maybe_import_lazy(module_name: str) -> ModuleType | None:
    """
    Try to lazily import a module by name. Returns a proxy that loads on first use,
        or None if unavailable.

    Results are cached for efficiency.
    """
    if module_name in sys.modules:
        return sys.modules[module_name]

    try:
        spec = find_spec(module_name)
        if spec is None:
            return None

        proxy = LazyModule(module_name)
        sys.modules[module_name] = proxy
        return proxy
    except (ModuleNotFoundError, ImportError) as e:
        logger.debug(_make_message(module_name, e))
        return None


@cache
def maybe_import(module_name: str) -> ModuleType | None:
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        logger.debug(_make_message(module_name, e))
        return None
