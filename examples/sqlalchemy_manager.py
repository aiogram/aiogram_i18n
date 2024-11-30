import logging
from asyncio import run
from os import environ
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject, User
from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.managers import BaseManager


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)
    language: Mapped[str] = mapped_column(String(2), nullable=False)
    ...


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, telegram_user: User, language: str) -> User:
        ...

    async def get_user(self, user_id: int) -> UserModel | None:
        ...

    async def commit(self):
        await self.session.commit()


class UserManager(BaseManager):
    async def set_locale(self, locale: str, user: UserModel, database: Database) -> None:
        user.language = locale
        await database.commit()

    async def get_locale(self, user: UserModel) -> str:
        return user.language


class DatabaseMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session_pool: async_sessionmaker[AsyncSession] = data["session_pool"]
        async with session_pool() as session:
            data["database"] = Database(
                session=session,
            )
            return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    def __init__(self, i18n_middleware: I18nMiddleware):
        self.i18n_middleware = i18n_middleware

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        # get data from event
        event_user: User = data["event_from_user"]
        database: Database = data["database"]

        # get user from the database
        user = await database.get_user(user_id=event_user.id)
        if not user:

            # match user language
            user_language = event_user.language_code
            if user_language not in self.i18n_middleware.core.available_locales:
                user_language = self.i18n_middleware.core.default_locale

            # create new user
            user = await database.create_user(
                telegram_user=event_user,
                language=user_language,
            )

        # update data and return handler
        data["user"] = user
        return await handler(event, data)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    bot = Bot(
        token=environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    mw = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}/LC_MESSAGES",
        ),
        manager=UserManager(),
    )
    dp.update.outer_middleware(DatabaseMiddleware())
    dp.update.outer_middleware(UserMiddleware(i18n_middleware=mw))
    mw.setup(dispatcher=dp)
    await dp.start_polling(bot, session_pool=1)


run(main())
