from __future__ import annotations

from typing import Final


DEFAULT_LANGUAGE: Final[str] = "ru"
SUPPORTED_LANGUAGES: Final[set[str]] = {"ru", "kk", "en"}

NO_RESULTS_MESSAGES: Final[dict[str, str]] = {
    "ru": (
        "🤔 По этому вопросу ничего не нашлось.\n\n"
        "Попробуй:\n"
        "• Переформулировать вопрос\n"
        "• Использовать ключевые слова (например, «стипендия», «дедлайн», «общежитие»)\n"
        "• Задать вопрос на другом языке\n\n"
        "Я лучше всего отвечаю на вопросы об учёбе, документах, дедлайнах и студенческой жизни."
    ),
    "kk": (
        "🤔 Бұл сұрақ бойынша ештеңе табылмады.\n\n"
        "Мынаны көріңіз:\n"
        "• Сұрақты қайта тұжырымдаңыз\n"
        "• Кілт сөздерді қолданыңыз (мысалы, «стипендия», «дедлайн», «жатақхана»)\n"
        "• Басқа тілде сұрап көріңіз\n\n"
        "Мен оқу, құжаттар, дедлайндар мен студенттік өмір туралы сұрақтарға жақсы жауап беремін."
    ),
    "en": (
        "🤔 No relevant messages found for your question.\n\n"
        "Try:\n"
        "• Rephrasing your question\n"
        '• Using keywords (e.g., "scholarship", "deadline", "housing")\n'
        "• Asking in a different language\n\n"
        "I work best with questions about academics, documents, deadlines, and student life."
    ),
}


def detect_language(text: str, telegram_language_code: str | None = None) -> str:
    """Detect whether the user is writing in Russian, Kazakh, or English."""
    normalized_text = (text or "").strip().lower()

    if _contains_kazakh_specific_letters(normalized_text):
        return "kk"

    if _contains_cyrillic(normalized_text):
        return "ru"

    if _contains_latin_letters(normalized_text):
        return "en"

    normalized_telegram_code = normalize_language_code(telegram_language_code)
    if normalized_telegram_code is not None:
        return normalized_telegram_code

    return DEFAULT_LANGUAGE


def get_no_results_message(text: str, telegram_language_code: str | None = None) -> str:
    language = detect_language(text, telegram_language_code=telegram_language_code)
    return NO_RESULTS_MESSAGES[language]


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


def _contains_kazakh_specific_letters(text: str) -> bool:
    return any(char in text for char in "әіңғүұқөһ")


def _contains_cyrillic(text: str) -> bool:
    return any("а" <= char <= "я" or char == "ё" for char in text)


def _contains_latin_letters(text: str) -> bool:
    return any("a" <= char <= "z" for char in text)
