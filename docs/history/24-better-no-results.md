# Feature: Better No-Results Message

## Problem

When search returns zero results, the bot replies with a dead-end message: "No relevant messages found for your question." The user has no idea what to do next — should they rephrase? Is the bot broken? Is the topic not covered?

## Solution

Replace the dead-end with a helpful message that:
1. Acknowledges the query didn't match anything
2. Suggests the user try rephrasing or asking differently
3. Gives a hint about what topics the bot knows about

## Technical Design

### Message Template

```python
NO_RESULTS_MESSAGES = {
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
        "• Using keywords (e.g., \"scholarship\", \"deadline\", \"housing\")\n"
        "• Asking in a different language\n\n"
        "I work best with questions about academics, documents, deadlines, and student life."
    ),
}
```

### Integration

In `dm_handler` and `ask_command`, replace the current no-results string:

```python
if not results:
    lang = get_user_language(user_id)  # from user_preferences or detect
    await update.message.reply_text(NO_RESULTS_MESSAGES[lang])
```

### Language Detection

- If user has preferences (feature 17), use stored language
- Otherwise, fall back to auto-detection from query (feature 14)
- If neither is available, default to Russian

## Files to Change

- `src/handlers/messages.py` — update no-results response in `dm_handler`
- `src/handlers/commands.py` — update no-results response in `ask_command`
- Optionally add templates to `src/services/language.py` (feature 14) if it exists

## Implementation Checklist

- [ ] Define no-results message templates in all three languages
- [ ] Replace dead-end messages in `dm_handler` and `ask_command`
- [ ] Use user's language preference if available
- [ ] Test: vague query with no results → helpful suggestions shown
- [ ] Test: messages display correctly in all three languages

## Status

Planned
