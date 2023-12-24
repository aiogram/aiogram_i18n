from typing import Any, Dict, List, Optional, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from aiogram_i18n import I18nContext, I18nMiddleware
from aiogram_i18n.lazy.base import BaseLazyFilter

INLINE_MARKUP = List[List[InlineKeyboardButton]]


class LanguageCallbackFilter(BaseLazyFilter):
    keyboard: "LanguageInlineMarkup"
    len: int

    def __init__(self, keyboard: "LanguageInlineMarkup"):
        self.keyboard = keyboard
        self.len = len(keyboard.prefix)

    async def startup(self, middleware: "I18nMiddleware") -> None:
        await self.keyboard.startup(middleware=middleware)

    async def __call__(self, callback: CallbackQuery) -> Union[bool, Dict[str, Any]]:
        if not callback.data or not callback.data.startswith(self.keyboard.prefix):
            return False
        return {self.keyboard.param: callback.data[self.len:]}


class LanguageInlineMarkup:
    def __init__(
        self,
        key: str,
        row: int = 3,
        hide_current: bool = False,
        prefix: str = "__lang__",
        param: str = "lang",
        keyboard: Optional[INLINE_MARKUP] = None,
    ):
        self.key = key
        self.row = row
        self.hide_current = hide_current
        self.prefix = prefix
        self.param = param
        self.filter = LanguageCallbackFilter(keyboard=self)
        self.keyboards: Dict[str, INLINE_MARKUP] = {}
        self.keyboard: Optional[INLINE_MARKUP] = keyboard or list()  # noqa: C408

    def reply_markup(self, locale: Optional[str] = None) -> InlineKeyboardMarkup:
        if locale is None:
            locale = I18nContext.get_current(False).locale
        return InlineKeyboardMarkup(
            inline_keyboard=self.keyboards.get(locale) or list()  # noqa: C408
        )

    async def startup(self, middleware: "I18nMiddleware") -> None:
        if self.keyboards:
            return
        for locale in middleware.core.available_locales:
            button = InlineKeyboardButton(
                text=middleware.core.get(self.key, locale),
                callback_data=f"{self.prefix}{locale}",
            )
            for _locale in middleware.core.available_locales:
                if self.hide_current and locale == _locale:
                    continue

                if _locale not in self.keyboards:
                    self.keyboards[_locale] = [[]]

                if len(self.keyboards[_locale][-1]) == self.row:
                    self.keyboards[_locale].append([])

                self.keyboards[_locale][-1].append(button)
        if not self.keyboard:
            return
        for keyboard in self.keyboards.values():
            keyboard.extend(self.keyboard)
