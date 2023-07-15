from gettext import GNUTranslations
from typing import Dict, Any

from aiogram_i18n.cores.base import BaseCore


class BabelCore(BaseCore[GNUTranslations]):
    def __init__(
        self, *,
        path: str,
        default_locale: str = "en"
    ) -> None:
        super().__init__()
        self.path = path
        self.default_locale = default_locale

    def find_locales(self) -> Dict[str, GNUTranslations]:
        """
        Load all compiled locales from path

        :return: dict with locales
        """
        translations: Dict[str, GNUTranslations] = {}
        locales = self._extract_locales(self.path)
        for locale, paths in self._find_locales(self.path, locales, ".mo").items():
            trans = translations[locale] = GNUTranslations()
            for path in paths:
                with open(path, "rb") as fp:
                    trans._parse(fp=fp) # noqa

        return translations

    def get(self, key: str, /, locale: str, **kwargs: Any) -> str:
        translator = self.get_translator(locale=locale)
        return translator.gettext(key).format(**kwargs)