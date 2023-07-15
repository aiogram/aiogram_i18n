from typing import Dict, Callable, Optional, Any, cast

from aiogram_i18n.exceptions import NoModuleError

try:
    from fluent.runtime import FluentBundle, FluentResource
except ImportError:
    raise NoModuleError(core_name="FluentRuntimeCore", module_name="fluent.runtime")

from aiogram_i18n.cores.base import BaseCore


class FluentRuntimeCore(BaseCore[FluentBundle]):
    def __init__(
        self,
        path: str, default_locale: str = "en",
        use_isolating: bool = True,
        functions: Optional[Dict[str, Callable[..., Any]]] = None,
        pre_compile: bool = True,
        raise_key_error: bool = True
    ) -> None:
        super().__init__()
        self.path = path
        self.use_isolating = use_isolating
        self.functions = functions
        self.default_locale = default_locale
        self.pre_compile = pre_compile,
        self.raise_key_error = raise_key_error

    def get(self, key: str, /, locale: str, **kwargs: Any) -> str:
        translator: FluentBundle = self.get_translator(locale=locale)
        message = translator.get_message(message_id=key)
        if message.value is None:
            if self.raise_key_error:
                raise KeyError("Key", key, "not found")
            return key
        text, errors = translator.format_pattern(
            pattern=message.value,
            args=kwargs
        )
        if errors:
            raise errors[0]
        return cast(str, text)

    def find_locales(self) -> Dict[str, FluentBundle]:
        translations: Dict[str, FluentBundle] = {}
        locales = self._extract_locales(self.path)

        for locale, paths in self._find_locales(self.path, locales, ".ftl").items():
            translations[locale] = FluentBundle(
                locales=[locale],
                use_isolating=self.use_isolating,
                functions=self.functions
            )

            for path in paths:
                with open(path, "r", encoding="utf8") as fp:
                    translations[locale].add_resource(FluentResource(fp.read()))

            if self.pre_compile:
                self.__compile_runtime(translations[locale])

        return translations

    @staticmethod
    def __compile_runtime(fb: FluentBundle) -> None:
        for key, value in fb._messages.items():  # noqa
            if key not in fb._compiled:  # noqa
                fb._compiled[key] = fb._compiler(value)  # noqa
        for key, value in fb._terms.items():  # noqa
            key = f"-{key}"
            if key not in fb._compiled:  # noqa
                fb._compiled[key] = fb._compiler(value)  # noqa
