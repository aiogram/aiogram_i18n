# aiogram_i18n

Installation:
```pip install aiogram_i18n```

To use FluentCompileCore:
```pip install fluent_compiler```

To use FluentRuntimeCore:
```pip install fluent.runtime```

```python
import asyncio
from contextlib import suppress
from logging import basicConfig, INFO
from typing import Any

from aiogram import Router, Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_i18n import I18nContext, LazyProxy, I18nMiddleware, LazyFilter
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from aiogram_i18n.types import (
    ReplyKeyboardMarkup, KeyboardButton
    # you should import mutable objects from here if you want to use LazyProxy in them
)

router = Router(name=__name__)
rkb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=LazyProxy("help"))]  # or L.help()
    ], resize_keyboard=True
)


@router.message(CommandStart())
async def cmd_start(message: Message, i18n: I18nContext) -> Any:
    name = message.from_user.mention_html()
    return message.reply(
        text=i18n.get("hello", user=name),  # or i18n.hello(user=name)
        reply_markup=rkb
    )


@router.message(LazyFilter("help"))  # or LazyProxy("help") or F.text == LazyProxy("help")
async def cmd_help(message: Message) -> Any:
    return message.reply(text="-- " + message.text + " --")


async def main() -> None:
    basicConfig(level=INFO)
    bot = Bot("42:ABC", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}/LC_MESSAGES"
        )
    )

    dp = Dispatcher()
    dp.include_router(router)
    i18n_middleware.setup(dispatcher=dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
```
