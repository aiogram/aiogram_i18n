from importlib import import_module
from typing import TYPE_CHECKING, Any, cast

from .base import BaseCore

if TYPE_CHECKING:
    from .fluent_compile_core import FluentCompileCore
    from .fluent_runtime_core import FluentRuntimeCore
    from .gnu_text_core import GNUTextCore
    from .jinja2_core import Jinja2Core


__cores__ = {
    "GNUTextCore": ".gnu_text_core",
    "FluentRuntimeCore": ".fluent_runtime_core",
    "FluentCompileCore": ".fluent_compile_core",
    "Jinja2Core": ".jinja2_core",
}

__all__ = (
    "GNUTextCore",
    "FluentRuntimeCore",
    "FluentCompileCore",
    "Jinja2Core",
    "BaseCore",
)


def __getattr__(name: str) -> BaseCore[Any]:
    if name not in __all__:
        raise AttributeError
    return cast(BaseCore[Any], getattr(import_module(__cores__[name], "aiogram_i18n.cores"), name))
