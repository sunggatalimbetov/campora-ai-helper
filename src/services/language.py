from __future__ import annotations

from typing import Final


DEFAULT_LANGUAGE: Final[str] = "ru"
SUPPORTED_LANGUAGES: Final[set[str]] = {"ru", "kk", "en"}
LANGUAGE_LABELS: Final[dict[str, str]] = {
    "ru": "Русский",
    "kk": "Қазақша",
    "en": "English",
}
KAZAKH_WORD_MARKERS: Final[tuple[str, ...]] = (
    "кашан",
    "калай",
    "кандай",
    "неге",
    "ушин",
    "келеси",
    "казир",
    "бугин",
    "ертен",
    "жок",
    "барма",
    "жатакхана",
    "кужат",
    "кужаттар",
    "сурак",
)

STRINGS: Final[dict[str, dict[str, str]]] = {
    "ru": {
        "searching": "🔍 Ищу, подожди...",
        "error": "❌ Произошла ошибка. Попробуй ещё раз.",
        "no_results": (
            "🤔 По этому вопросу ничего не нашлось.\n\n"
            "Попробуй:\n"
            "• Переформулировать вопрос\n"
            "• Использовать ключевые слова (например, «стипендия», «дедлайн», «общежитие»)\n"
            "• Задать вопрос на другом языке\n\n"
            "Я лучше всего отвечаю на вопросы об учёбе, документах, дедлайнах и студенческой жизни."
        ),
        "ask_private_only": "Эта команда работает только в группах. В личке просто отправь вопрос сообщением.",
        "ask_usage": "Использование: /ask <твой вопрос>",
        "new_session": "🔄 Разговор сброшен. Следующий вопрос начнёт новую сессию.",
        "help": (
            "🤖 *Vectir AI*\n\n"
            "*В группах:*\n"
            "• `/ask <вопрос>` - задать вопрос по истории чата\n"
            "• `/new` - начать новый разговор\n"
            "• `/help` - показать помощь\n\n"
            "*В личке:*\n"
            "• Просто отправь вопрос сообщением\n"
            "• `/new` - начать новый разговор\n"
            "• `/language` - изменить язык интерфейса\n"
            "• `/help` - показать помощь\n\n"
            "Бот запоминает недавние вопросы, поэтому можно задавать уточнения."
        ),
        "start_group": "👋 В личке я помогу искать ответы по истории чатов. Напиши мне напрямую, чтобы начать.",
        "start_ready": "👋 С возвращением! Просто напиши свой вопрос.",
        "start_welcome": (
            "👋 Привет! Я Vectir AI.\n\n"
            "Помогаю искать ответы по истории университетских чатов. "
            "Сначала выбери язык интерфейса."
        ),
        "choose_language": "Выбери язык интерфейса:",
        "language_command": "🌐 *Язык интерфейса*\n\nСейчас: *{language}*\n\nВыбери новый язык:",
        "language_updated": "✅ Язык интерфейса изменён на {language}.",
    },
    "kk": {
        "searching": "🔍 Іздеп жатырмын, күте тұрыңыз...",
        "error": "❌ Қате пайда болды. Қайтадан көріңіз.",
        "no_results": (
            "🤔 Бұл сұрақ бойынша ештеңе табылмады.\n\n"
            "Мынаны көріңіз:\n"
            "• Сұрақты қайта тұжырымдаңыз\n"
            "• Кілт сөздерді қолданыңыз (мысалы, «стипендия», «дедлайн», «жатақхана»)\n"
            "• Басқа тілде сұрап көріңіз\n\n"
            "Мен оқу, құжаттар, дедлайндар мен студенттік өмір туралы сұрақтарға жақсы жауап беремін."
        ),
        "ask_private_only": "Бұл команда тек топта жұмыс істейді. Жекеде сұрағыңызды жай хабарлама ретінде жіберіңіз.",
        "ask_usage": "Қолданылуы: /ask <сұрағыңыз>",
        "new_session": "🔄 Әңгіме тазартылды. Келесі сұрақ жаңа сессияны бастайды.",
        "help": (
            "🤖 *Vectir AI*\n\n"
            "*Топтарда:*\n"
            "• `/ask <сұрақ>` - чат тарихы бойынша сұрақ қою\n"
            "• `/new` - жаңа әңгімені бастау\n"
            "• `/help` - көмекті көрсету\n\n"
            "*Жекеде:*\n"
            "• Сұрақты жай хабарлама ретінде жіберіңіз\n"
            "• `/new` - жаңа әңгімені бастау\n"
            "• `/language` - интерфейс тілін өзгерту\n"
            "• `/help` - көмекті көрсету\n\n"
            "Бот соңғы сұрақтарды есте сақтайды, сондықтан нақтылап сұрай аласыз."
        ),
        "start_group": "👋 Жекеде мен чат тарихынан жауап іздеуге көмектесемін. Бастау үшін маған жеке жазыңыз.",
        "start_ready": "👋 Қайта келгеніңізге қуаныштымын! Сұрағыңызды жаза беріңіз.",
        "start_welcome": (
            "👋 Сәлем! Мен Vectir AI.\n\n"
            "Университет чаттарының тарихынан жауап табуға көмектесемін. "
            "Алдымен интерфейс тілін таңдаңыз."
        ),
        "choose_language": "Интерфейс тілін таңдаңыз:",
        "language_command": "🌐 *Интерфейс тілі*\n\nҚазір: *{language}*\n\nЖаңа тілді таңдаңыз:",
        "language_updated": "✅ Интерфейс тілі {language} болып өзгертілді.",
    },
    "en": {
        "searching": "🔍 Searching, please wait...",
        "error": "❌ Sorry, something went wrong. Please try again.",
        "no_results": (
            "🤔 No relevant messages found for your question.\n\n"
            "Try:\n"
            "• Rephrasing your question\n"
            '• Using keywords (e.g., "scholarship", "deadline", "housing")\n'
            "• Asking in a different language\n\n"
            "I work best with questions about academics, documents, deadlines, and student life."
        ),
        "ask_private_only": "This command works only in group chats. In private messages, just send your question directly.",
        "ask_usage": "Usage: /ask <your question>",
        "new_session": "🔄 Conversation reset. Your next question will start a fresh session.",
        "help": (
            "🤖 *Vectir AI*\n\n"
            "*In Groups:*\n"
            "• `/ask <question>` - ask about the chat history\n"
            "• `/new` - start a fresh conversation\n"
            "• `/help` - show help\n\n"
            "*In Private Messages:*\n"
            "• Just send your question directly\n"
            "• `/new` - start a fresh conversation\n"
            "• `/language` - change interface language\n"
            "• `/help` - show help\n\n"
            "The bot remembers recent questions so you can ask follow-ups naturally."
        ),
        "start_group": "👋 In DMs I can help search past chat history. Message me directly to get started.",
        "start_ready": "👋 Welcome back! Just send your question.",
        "start_welcome": (
            "👋 Hi! I'm Vectir AI.\n\n"
            "I help find answers from university chat history. "
            "First, choose your interface language."
        ),
        "choose_language": "Choose your interface language:",
        "language_command": "🌐 *Interface Language*\n\nCurrent: *{language}*\n\nChoose a new language:",
        "language_updated": "✅ Interface language changed to {language}.",
    },
}


def detect_language(text: str, telegram_language_code: str | None = None) -> str:
    """Detect whether the user is writing in Russian, Kazakh, or English."""
    normalized_text = (text or "").strip().lower()

    if _contains_kazakh_specific_letters(normalized_text):
        return "kk"

    if _contains_kazakh_word_markers(normalized_text):
        return "kk"

    if _contains_cyrillic(normalized_text):
        return "ru"

    if _contains_latin_letters(normalized_text):
        return "en"

    normalized_telegram_code = normalize_language_code(telegram_language_code)
    if normalized_telegram_code is not None:
        return normalized_telegram_code

    return DEFAULT_LANGUAGE


def normalize_language_code(language_code: str | None) -> str | None:
    if not language_code:
        return None

    normalized_code = language_code.strip().lower().replace("-", "_")

    if normalized_code.startswith("kk"):
        return "kk"
    if normalized_code.startswith("ru"):
        return "ru"
    if normalized_code.startswith("en"):
        return "en"

    return None


def resolve_ui_language(
    preferred_language: str | None,
    query_text: str | None = None,
    telegram_language_code: str | None = None,
) -> str:
    normalized_preference = normalize_language_code(preferred_language)
    if normalized_preference is not None:
        return normalized_preference

    if query_text and query_text.strip():
        return detect_language(query_text, telegram_language_code=telegram_language_code)

    normalized_telegram_code = normalize_language_code(telegram_language_code)
    if normalized_telegram_code is not None:
        return normalized_telegram_code

    return DEFAULT_LANGUAGE


def resolve_query_language(text: str, telegram_language_code: str | None = None) -> str:
    return detect_language(text, telegram_language_code=telegram_language_code)


def get_string(language: str, key: str, **kwargs) -> str:
    lang = normalize_language_code(language) or DEFAULT_LANGUAGE
    template = STRINGS.get(lang, STRINGS[DEFAULT_LANGUAGE]).get(key, STRINGS[DEFAULT_LANGUAGE][key])
    return template.format(**kwargs)


def get_language_label(language: str) -> str:
    lang = normalize_language_code(language) or DEFAULT_LANGUAGE
    return LANGUAGE_LABELS.get(lang, LANGUAGE_LABELS[DEFAULT_LANGUAGE])


def _contains_kazakh_specific_letters(text: str) -> bool:
    return any(char in text for char in "әіңғүұқөһ")


def _contains_cyrillic(text: str) -> bool:
    return any("а" <= char <= "я" or char == "ё" for char in text)


def _contains_latin_letters(text: str) -> bool:
    return any("a" <= char <= "z" for char in text)


def _contains_kazakh_word_markers(text: str) -> bool:
    words = set(text.split())
    return any(marker in words for marker in KAZAKH_WORD_MARKERS)
