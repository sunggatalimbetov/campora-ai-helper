# Feature: Onboarding Flow for First-Time DM Users

## Problem

When a user opens a DM with the bot for the first time, they get a generic welcome message and no guidance on scope. They don't know which groups are indexed, and the bot searches all groups indiscriminately. This leads to irrelevant results and a confusing first experience.

## Solution

Replace the current `/start` message with a 3-step onboarding flow:

1. **Welcome** — brief intro explaining what the bot does
2. **Group selection** — two inline buttons: UNIME / NU. Auto-select if only one applies (future: auto-detect from scraped data)
3. **Language preference** — three buttons: Русский / Қазақша / English

Store preferences in a new `user_preferences` table. If a user skips onboarding or sends a question immediately, fall back to current behavior (all groups, auto-detect language from query).

## Technical Design

### Database

New table `user_preferences`:

```sql
CREATE TABLE user_preferences (
    user_id BIGINT PRIMARY KEY,
    selected_group TEXT,          -- 'unime' | 'nu' | NULL (all groups)
    language TEXT DEFAULT 'ru',   -- 'ru' | 'kk' | 'en'
    onboarded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Onboarding Flow

**Step 1 — Welcome (on `/start`):**

```
👋 Привет! Я Vectir AI — помогу найти ответы на вопросы по истории переписки университетских чатов.

Для начала выбери свой университет:
```

Two inline buttons: `[UNIME]` `[NU]`

**Step 2 — After group selection:**

```
Отлично! Выбери язык, на котором тебе удобнее общаться:
```

Three inline buttons: `[Русский]` `[Қазақша]` `[English]`

**Step 3 — Confirmation:**

```
Готово! Задавай любой вопрос — просто напиши мне сообщение.

Команды:
• /new — начать новый разговор
• /settings — изменить университет или язык
• /help — помощь
```

### Handler Logic

```python
# src/handlers/onboarding.py

async def start_command(update, context):
    user_id = update.effective_user.id
    prefs = get_user_preferences(user_id)

    if prefs and prefs.get("onboarded_at"):
        # Returning user — show short welcome
        await update.message.reply_text("👋 С возвращением! Просто напиши свой вопрос.")
        return

    # New user — start onboarding
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("UNIME", callback_data="onboard:group:unime"),
         InlineKeyboardButton("NU", callback_data="onboard:group:nu")]
    ])
    await update.message.reply_text(WELCOME_TEXT, reply_markup=keyboard)


async def onboard_group_callback(update, context):
    query = update.callback_query
    await query.answer()
    group = query.data.split(":")[2]
    save_user_preference(query.from_user.id, "selected_group", group)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Русский", callback_data="onboard:lang:ru"),
         InlineKeyboardButton("Қазақша", callback_data="onboard:lang:kk"),
         InlineKeyboardButton("English", callback_data="onboard:lang:en")]
    ])
    await query.edit_message_text(LANGUAGE_PROMPT, reply_markup=keyboard)


async def onboard_lang_callback(update, context):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[2]
    save_user_preference(query.from_user.id, "language", lang)
    mark_onboarded(query.from_user.id)
    await query.edit_message_text(CONFIRMATION_TEXT)
```

### Integration with Search

Once the user has a `selected_group`, pass the corresponding `chat_id` to `search_messages()` in `dm_handler`. This ties into feature 13 (group-scoped search).

### Edge Cases

- **User sends a question before finishing onboarding**: treat as unonboarded, search all groups, auto-detect language. Don't block the user from asking questions.
- **User presses /start again after onboarding**: show short "welcome back" message, not the full flow.
- **Mapping group names to chat_ids**: maintain a simple mapping dict in config or a `groups` table. For now, hardcode UNIME and NU chat_ids in settings.

## Files to Change

- Create `src/handlers/onboarding.py` — onboarding flow handlers
- Create `src/services/user_preferences.py` — CRUD for user_preferences table
- `src/handlers/commands.py` — replace `start_command` with onboarding version
- `src/handlers/messages.py` — read user preferences to scope search + set language
- `src/config/settings.py` — add group name → chat_id mapping
- `main.py` — register new callback handlers
- `sql/` — migration for `user_preferences` table

## Implementation Checklist

- [ ] Write SQL migration for `user_preferences` table
- [ ] Create `src/services/user_preferences.py` with get/save/mark_onboarded
- [ ] Create `src/handlers/onboarding.py` with start + callback handlers
- [ ] Add group name → chat_id mapping to settings
- [ ] Register onboarding callback handlers in `main.py`
- [ ] Update `dm_handler` to read user preferences
- [ ] Test: new user → full onboarding flow
- [ ] Test: returning user → short welcome
- [ ] Test: user sends question before finishing onboarding → still works

## Status

Planned
