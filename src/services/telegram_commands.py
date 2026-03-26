from telegram import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats, BotCommandScopeChat
from telegram.ext import Application

from src.services.language import normalize_language_code


PRIVATE_COMMANDS_BY_LANGUAGE: dict[str, list[BotCommand]] = {
    "ru": [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Показать помощь"),
        BotCommand("new", "Начать новый разговор"),
        BotCommand("language", "Изменить язык интерфейса"),
        BotCommand("optout", "Удалить сообщения из индексации"),
        BotCommand("optin", "Снова включить индексацию"),
    ],
    "kk": [
        BotCommand("start", "Ботты іске қосу"),
        BotCommand("help", "Көмекті көрсету"),
        BotCommand("new", "Жаңа әңгімені бастау"),
        BotCommand("language", "Интерфейс тілін өзгерту"),
        BotCommand("optout", "Хабарламаларды индекстеуден алып тастау"),
        BotCommand("optin", "Индекстеуді қайта қосу"),
    ],
    "en": [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
        BotCommand("new", "Start a fresh conversation"),
        BotCommand("language", "Change interface language"),
        BotCommand("optout", "Remove your messages from indexing"),
        BotCommand("optin", "Enable indexing for your messages again"),
    ],
}

GROUP_COMMANDS: list[BotCommand] = [
    BotCommand("ask", "Ask a question about the group history"),
    BotCommand("help", "Show help"),
    BotCommand("new", "Start a fresh conversation"),
    BotCommand("optout", "Remove your messages from indexing"),
    BotCommand("optin", "Enable indexing for your messages again"),
]


def get_private_commands(language: str | None) -> list[BotCommand]:
    normalized_language = normalize_language_code(language) or "en"
    return PRIVATE_COMMANDS_BY_LANGUAGE[normalized_language]


async def register_default_bot_commands(app: Application) -> None:
    """Register default slash commands used before a user chooses a UI language."""
    await app.bot.set_my_commands(get_private_commands("en"), scope=BotCommandScopeAllPrivateChats())
    await app.bot.set_my_commands(GROUP_COMMANDS, scope=BotCommandScopeAllGroupChats())


async def register_private_chat_commands(app: Application, chat_id: int, language: str | None) -> None:
    """Register slash commands for a specific private chat in the selected UI language."""
    await app.bot.set_my_commands(get_private_commands(language), scope=BotCommandScopeChat(chat_id))
