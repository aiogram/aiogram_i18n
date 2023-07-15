
from . import types
from .context import I18nContext
from .lazy import LazyProxy, LazyFactory
from .middleware import I18nMiddleware

L = LazyFactory()

__all__ = (
    "__version__",
    "types",
    "I18nContext",
    "LazyProxy",
    "I18nMiddleware",
    "L"
)

__version__ = "1.0"