from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand("get_weather", "Получить прогноз погоды в итересующем городе"),
            BotCommand("bot_stat", "Статистика, которую собирает бот")
        ],
        scope=BotCommandScopeDefault()
    )