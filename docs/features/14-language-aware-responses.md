# Feature: Language-Aware Responses

## Problem

The bot serves Kazakh and CIS university students who write in Russian, Kazakh, and English. While the system prompt in `generate_answer.py` already instructs GPT to "write your response in the same language as the user's question," there are inconsistencies:

- Hardcoded UI messages are in English or Russian only (e.g., "🔍 Searching, please wait...")
- Error messages are always in English
- The welcome message is Russian-only
- Query rewriting doesn't consider language preservation explicitly

## Solution

Make all bot-generated UI messages language-aware by detecting the user's language and serving appropriate strings.

## Technical Design

### Approach: Simple Language Detection

Rather than a full i18n framework, use a lightweight approach:

1. Detect language from the user's message (first message in session or current message)
2. Use a string map for UI messages

```python
# src/services/language.py

from src.services.message_search._clients import client_oa

STRINGS = {
    "ru": {
        "searching": "🔍 Ищу, подожди...",
        "no_results": "❌ Не нашёл подходящих сообщений по твоему вопросу.",
        "error": "❌ Произошла ошибка. Попробуй ещё раз.",
        "rate_limit": "⏳ Слишком много запросов. Подожди немного.",
    },
    "kk": {
        "searching": "🔍 Іздеп жатырмын, күте тұрыңыз...",
        "no_results": "❌ Сұрағыңызға сәйкес хабарлама табылмады.",
        "error": "❌ Қате пайда болды. Қайтадан көріңіз.",
        "rate_limit": "⏳ Сұраныстар тым көп. Біраз күтіңіз.",
    },
    "en": {
        "searching": "🔍 Searching, please wait...",
        "no_results": "❌ No relevant messages found for your question.",
        "error": "❌ Sorry, something went wrong. Please try again.",
        "rate_limit": "⏳ Too many requests. Please wait a bit.",
    },
}


def detect_language(text: str) -> str:
    """Detect language of text. Returns 'ru', 'kk', or 'en'."""
    try:
        response = client_oa.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=5,
            messages=[
                {
                    "role": "system",
                    "content": "Detect the language of the text. Reply with exactly one of: ru, kk, en",
                },
                {"role": "user", "content": text[:200]},
            ],
        )
        lang = response.choices[0].message.content.strip().lower()
        return lang if lang in STRINGS else "ru"  # default to Russian
    except Exception:
        return "ru"


def get_string(lang: str, key: str) -> str:
    """Get localized string."""
    return STRINGS.get(lang, STRINGS["ru"]).get(key, STRINGS["ru"][key])
```

### Cost Consideration

An extra LLM call for language detection adds latency and cost. Alternatives:
- **Option A**: Use `langdetect` or `langid` Python library (free, fast, offline) — less accurate for short Kazakh text
- **Option B**: Use Telegram's `user.language_code` — unreliable, reflects phone settings not message language
- **Option C**: LLM call (most accurate, but adds ~200ms)

Recommend **Option A** with LLM fallback for ambiguous cases.

### Integration

Replace hardcoded strings in handlers with `get_string()`:

```python
lang = detect_language(query)
await update.message.reply_text(get_string(lang, "searching"))
```

## Files to Change

- Create `src/services/language.py` — language detection + string map
- `src/handlers/commands.py` — use localized strings
- `src/handlers/messages.py` — use localized strings
- `requirements.txt` — add `langdetect` if using Option A

## Implementation Checklist

- [ ] Create `src/services/language.py` with detection and string map
- [ ] Replace hardcoded strings in `ask_command` with `get_string()`
- [ ] Replace hardcoded strings in `dm_handler` with `get_string()`
- [ ] Test with Russian question → Russian UI messages
- [ ] Test with Kazakh question → Kazakh UI messages
- [ ] Test with English question → English UI messages
- [ ] Evaluate latency impact of language detection

## Status

Planned
