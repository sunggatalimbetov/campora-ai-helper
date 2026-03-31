from __future__ import annotations

from typing import Final


DEFAULT_LANGUAGE: Final[str] = "en"
SUPPORTED_LANGUAGES: Final[set[str]] = {"ru", "kk", "en"}
LANGUAGE_LABELS: Final[dict[str, str]] = {
    "ru": "Русский",
    "kk": "Қазақша",
    "en": "English",
}
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
        "mention_usage": "Упомяни меня и добавь вопрос. Пример: {bot_username} когда дедлайн подачи документов?",
        "new_session": "🔄 Разговор сброшен. Следующий вопрос начнёт новую сессию.",
        "help": (
            "🤖 *Campora AI*\n\n"
            "*В группах:*\n"
            "• `/ask <вопрос>` - задать вопрос по истории чата\n"
            "• `@bot <вопрос>` - спросить прямо в сообщении\n"
            "• `/new` - начать новый разговор\n"
            "• `/help` - показать помощь\n\n"
            "*В личке:*\n"
            "• Просто отправь вопрос сообщением\n"
            "• `/new` - начать новый разговор\n"
            "• `/settings` - настройки (университет, язык)\n"
            "• `/help` - показать помощь\n\n"
            "Бот запоминает недавние вопросы, поэтому можно задавать уточнения."
        ),
        "start_group": "👋 В личке я помогу искать ответы по истории чатов. Напиши мне напрямую, чтобы начать.",
        "start_ready": "👋 С возвращением! Просто напиши свой вопрос.",
        "start_welcome": (
            "👋 Привет! Я Campora AI.\n\n"
            "Помогаю искать ответы по истории университетских чатов."
        ),
        "choose_group": "Сначала выбери свой университет:",
        "choose_language": "Выбери язык интерфейса:",
        "group_updated": "✅ Университет выбран: {group_label}.",
        "language_command": "🌐 *Язык интерфейса*\n\nСейчас: *{language_label}*\n\nВыбери новый язык:",
        "language_updated": "✅ Язык интерфейса изменён на {language_label}.",
        "rate_limited": "⏳ Слишком много запросов. Подожди немного перед следующим вопросом.",
        "optout_success": "Готово. Твои сообщения удалены из базы и больше не будут индексироваться.",
        "optin_success": "Окей, теперь твои сообщения снова будут индексироваться.",
        "settings": "⚙️ Настройки\n\nУниверситет: {group_label}\nЯзык: {language_label}\n\nЧто хочешь изменить?",
        "settings_not_onboarded": "Сначала пройди настройку: /start",
        "settings_btn_university": "Университет",
        "settings_btn_language": "Язык",
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
        "mention_usage": "Мені атап, сұрақты жазыңыз. Мысалы: {bot_username} құжат тапсыру дедлайны қашан?",
        "new_session": "🔄 Әңгіме тазартылды. Келесі сұрақ жаңа сессияны бастайды.",
        "help": (
            "🤖 *Campora AI*\n\n"
            "*Топтарда:*\n"
            "• `/ask <сұрақ>` - чат тарихы бойынша сұрақ қою\n"
            "• `@bot <сұрақ>` - хабарламада тікелей сұрау\n"
            "• `/new` - жаңа әңгімені бастау\n"
            "• `/help` - көмекті көрсету\n\n"
            "*Жекеде:*\n"
            "• Сұрақты жай хабарлама ретінде жіберіңіз\n"
            "• `/new` - жаңа әңгімені бастау\n"
            "• `/settings` - баптаулар (университет, тіл)\n"
            "• `/help` - көмекті көрсету\n\n"
            "Бот соңғы сұрақтарды есте сақтайды, сондықтан нақтылап сұрай аласыз."
        ),
        "start_group": "👋 Жекеде мен чат тарихынан жауап іздеуге көмектесемін. Бастау үшін маған жеке жазыңыз.",
        "start_ready": "👋 Қайта келгеніңізге қуаныштымын! Сұрағыңызды жаза беріңіз.",
        "start_welcome": (
            "👋 Сәлем! Мен Campora AI.\n\n"
            "Университет чаттарының тарихынан жауап табуға көмектесемін."
        ),
        "choose_group": "Алдымен университетіңізді таңдаңыз:",
        "choose_language": "Интерфейс тілін таңдаңыз:",
        "group_updated": "✅ Университет таңдалды: {group_label}.",
        "language_command": "🌐 *Интерфейс тілі*\n\nҚазір: *{language_label}*\n\nЖаңа тілді таңдаңыз:",
        "language_updated": "✅ Интерфейс тілі {language_label} болып өзгертілді.",
        "rate_limited": "⏳ Сұраулар тым көп. Келесі сұрақ алдында аздап күтіңіз.",
        "optout_success": "Дайын. Сіздің хабарламаларыңыз базадан өшірілді және енді индекстелмейді.",
        "optin_success": "Жарайды, енді сіздің хабарламаларыңыз қайтадан индекстеледі.",
        "settings": "⚙️ Баптаулар\n\nУниверситет: {group_label}\nТіл: {language_label}\n\nНені өзгерткіңіз келеді?",
        "settings_not_onboarded": "Алдымен баптаудан өтіңіз: /start",
        "settings_btn_university": "Университет",
        "settings_btn_language": "Тіл",
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
        "mention_usage": "Mention me and include a question. Example: {bot_username} when is the application deadline?",
        "new_session": "🔄 Conversation reset. Your next question will start a fresh session.",
        "help": (
            "🤖 *Campora AI*\n\n"
            "*In Groups:*\n"
            "• `/ask <question>` - ask about the chat history\n"
            "• `@bot <question>` - ask directly in a message\n"
            "• `/new` - start a fresh conversation\n"
            "• `/help` - show help\n\n"
            "*In Private Messages:*\n"
            "• Just send your question directly\n"
            "• `/new` - start a fresh conversation\n"
            "• `/settings` - settings (university, language)\n"
            "• `/help` - show help\n\n"
            "The bot remembers recent questions so you can ask follow-ups naturally."
        ),
        "start_group": "👋 In DMs I can help search past chat history. Message me directly to get started.",
        "start_ready": "👋 Welcome back! Just send your question.",
        "start_welcome": (
            "👋 Hi! I'm Campora AI.\n\n"
            "I help find answers from university chat history."
        ),
        "choose_group": "First, choose your university:",
        "choose_language": "Choose your interface language:",
        "group_updated": "✅ University selected: {group_label}.",
        "language_command": "🌐 *Interface Language*\n\nCurrent: *{language_label}*\n\nChoose a new language:",
        "language_updated": "✅ Interface language changed to {language_label}.",
        "rate_limited": "⏳ Too many requests. Please wait a bit before asking again.",
        "optout_success": "Done. Your messages were removed from the database and will no longer be indexed.",
        "optin_success": "Okay, your messages will now be indexed again.",
        "settings": "⚙️ Settings\n\nUniversity: {group_label}\nLanguage: {language_label}\n\nWhat would you like to change?",
        "settings_not_onboarded": "Please complete setup first: /start",
        "settings_btn_university": "University",
        "settings_btn_language": "Language",
    },
}
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


def detect_language_from_text(text: str) -> str | None:
    """Detect language from text using character frequency heuristic."""
    if not text or len(text.strip()) < 3:
        return None

    cyrillic = 0
    latin = 0
    kazakh_specific = 0

    for ch in text:
        if "\u0400" <= ch <= "\u04ff":
            cyrillic += 1
            if ch in "ӘәҒғҚқҢңӨөҰұҮүҺһІі":
                kazakh_specific += 1
        elif "a" <= ch.lower() <= "z":
            latin += 1

    total = cyrillic + latin
    if total < 3:
        return None

    if cyrillic > latin:
        if kazakh_specific >= 1:
            return "kk"
        return "ru"
    if latin > cyrillic:
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

    detected = detect_language_from_text(query_text) if query_text else None
    if detected is not None:
        return detected

    normalized_telegram = normalize_language_code(telegram_language_code)
    if normalized_telegram is not None:
        return normalized_telegram

    return DEFAULT_LANGUAGE


def get_string(language: str, key: str, **kwargs) -> str:
    lang = normalize_language_code(language) or DEFAULT_LANGUAGE
    template = STRINGS.get(lang, STRINGS[DEFAULT_LANGUAGE]).get(key, STRINGS[DEFAULT_LANGUAGE][key])
    return template.format(**kwargs)


def get_language_label(language: str) -> str:
    lang = normalize_language_code(language) or DEFAULT_LANGUAGE
    return LANGUAGE_LABELS.get(lang, LANGUAGE_LABELS[DEFAULT_LANGUAGE])
