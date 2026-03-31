# How-To Guides

Practical recipes for common development tasks in campora-ai-helper.

---

## 1. Setting up the local development environment

### Prerequisites

- Python 3.9+
- A virtual environment (recommended: `python -m venv .venv && source .venv/bin/activate`)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An OpenAI API key
- A Supabase project with the required schema applied

### Environment variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your-bot-token
OPENAI_API_KEY=your-openai-api-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

Optional variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_MAX_REQUESTS` | `10` | Max requests per user per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `3600` | Rate limit window in seconds |
| `SIMILARITY_THRESHOLD` | `0.45` | Minimum cosine similarity for search results (0.0–1.0) |
| `SEARCH_SOURCE_OVERRIDES` | `{}` | JSON mapping of group chat IDs to source chat IDs (see section 4) |

### Installing dependencies

```bash
pip install -r requirements.txt
```

### Running database migrations

If you have the Supabase CLI installed and linked:

```bash
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

Migration files are in the `sql/` directory.

### Starting the bot

```bash
python main.py
```

The bot starts polling for updates. It retries automatically on network errors and Telegram API conflicts.

After making changes, run existing tests:

```bash
python3 -m unittest discover tests -v
```

---

## 2. Adding a new slash command

This walks through adding a `/mycommand` command as an example.

### Step 1: Create the handler function

Add your handler to `src/handlers/commands.py`. The existing imports at the top of the file provide the necessary functions (`get_user_language` from `src.services.user_preferences`, `resolve_ui_language` and `get_string` from `src.services.language`):

```python
async def mycommand_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mycommand."""
    preferred_language = get_user_language(update.effective_user.id)
    ui_language = resolve_ui_language(
        preferred_language,
        telegram_language_code=update.effective_user.language_code,
    )

    # Your logic here
    await update.message.reply_text(get_string(ui_language, "mycommand_response"))

# Note: telegram_language_code provides a fallback when preferred_language
# is None (e.g., for first-time users). See resolve_ui_language() in
# src/services/language.py for the full fallback chain.
```

If your command is complex enough to warrant a separate file, create it in `src/handlers/` and follow the same pattern.

### Step 2: Add UI strings for all languages

In `src/services/language.py`, add a key to the `STRINGS` dict for each language:

```python
"ru": {
    # ... existing strings ...
    "mycommand_response": "Ответ на команду",
},
"kk": {
    # ... existing strings ...
    "mycommand_response": "Команданың жауабы",
},
"en": {
    # ... existing strings ...
    "mycommand_response": "Command response",
},
```

### Step 3: Register the handler in main.py

In the `main()` function, add a `CommandHandler`:

```python
app.add_handler(CommandHandler("mycommand", mycommand_command))
```

Import your handler at the top of the file:

```python
from src.handlers.commands import mycommand_command
```

### Step 4: Register with Telegram's command menu

In `src/services/telegram_commands.py`, add the command to `PRIVATE_COMMANDS_BY_LANGUAGE` for each language:

```python
"ru": [
    # ... existing ...
    BotCommand("mycommand", "Описание команды"),
],
"kk": [
    # ... existing ...
    BotCommand("mycommand", "Команданың сипаттамасы"),
],
"en": [
    # ... existing ...
    BotCommand("mycommand", "Command description"),
],
```

If the command should also appear in group chats, add it to the `GROUP_COMMANDS` list instead.

### Checklist

- [ ] Handler function in `src/handlers/commands.py`
- [ ] UI strings in `src/services/language.py` (all 3 languages)
- [ ] `CommandHandler` registered in `main.py`
- [ ] `BotCommand` added to `src/services/telegram_commands.py` (all 3 languages)
- [ ] Import added to `main.py` if handler is in a new file

---

## 3. Adding a new language

This walks through adding French (`fr`) as an example.

### Step 1: Add to supported languages and labels

In `src/services/language.py`:

```python
SUPPORTED_LANGUAGES: Final[set[str]] = {"ru", "kk", "en", "fr"}

LANGUAGE_LABELS: Final[dict[str, str]] = {
    "ru": "Русский",
    "kk": "Қазақша",
    "en": "English",
    "fr": "Français",
}
```

### Step 2: Add all UI strings

Add a complete `"fr"` entry to the `STRINGS` dict. Copy all keys from an existing language and translate them:

```python
"fr": {
    "searching": "🔍 Recherche en cours...",
    "error": "❌ Une erreur s'est produite.",
    "no_results": "🤔 Aucun résultat pertinent trouvé.",
    "ask_usage": "Utilisation: /ask <votre question>",
    "ask_private_only": "Utilisez /ask dans un chat de groupe.",
    # ... all other keys from an existing language ...
},
```

Every key present in the other languages must be present in the new one. Missing keys will fall back to English.

### Step 3: Update language normalization

In `normalize_language_code()`, add a case for the new language prefix:

```python
def normalize_language_code(language_code: str | None) -> str | None:
    # ... existing code ...
    if normalized_code.startswith("fr"):
        return "fr"
    return None
```

This ensures that Telegram language codes like `"fr-FR"` are normalized to `"fr"`.

### Step 4: Add Telegram commands for the language

In `src/services/telegram_commands.py`, add a `"fr"` entry to `PRIVATE_COMMANDS_BY_LANGUAGE`:

```python
"fr": [
    BotCommand("start", "Démarrer le bot"),
    BotCommand("help", "Afficher l'aide"),
    BotCommand("new", "Démarrer une nouvelle conversation"),
    BotCommand("settings", "Paramètres (université, langue)"),
    BotCommand("optout", "Supprimer vos messages de l'indexation"),
    BotCommand("optin", "Réactiver l'indexation de vos messages"),
],
```

### Step 5: Update the database CHECK constraint

The `user_preferences.language` column has a CHECK constraint restricting values to the currently supported languages. Create a migration (e.g., `sql/011_add_french_language.sql`) to update it:

```sql
ALTER TABLE user_preferences DROP CONSTRAINT user_preferences_language_check;
ALTER TABLE user_preferences ADD CONSTRAINT user_preferences_language_check
    CHECK (language IN ('ru', 'kk', 'en', 'fr'));
```

Without this, saving the new language preference will fail with a constraint violation.

### Step 6: Add to the language selection keyboard

In `src/handlers/onboarding.py`, update `create_language_keyboard()`:

```python
def create_language_keyboard(prefix: str = LANGUAGE_CALLBACK_PREFIX) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Русский", callback_data=f"{prefix}ru"),
            InlineKeyboardButton("Қазақша", callback_data=f"{prefix}kk"),
            InlineKeyboardButton("English", callback_data=f"{prefix}en"),
            InlineKeyboardButton("Français", callback_data=f"{prefix}fr"),
        ]
    ])
```

If adding a 4th+ language, consider splitting the keyboard into multiple rows (2 per row) for better display on narrow mobile screens.

### Checklist

- [ ] Language added to `SUPPORTED_LANGUAGES` and `LANGUAGE_LABELS`
- [ ] All UI string keys translated in `STRINGS`
- [ ] `normalize_language_code()` handles the new prefix
- [ ] Database CHECK constraint updated via migration
- [ ] Telegram commands added in `telegram_commands.py`
- [ ] Language button added to the selection keyboard in `onboarding.py`

---

## 4. Configuring search source overrides

### What overrides do

By default, `/ask` searches the chat history of the group it's invoked in. Search source overrides let you redirect searches from one group to another. This is useful when a group's messages are scraped under a different chat ID (e.g., an archived group or a Telethon-scraped source).

### Setting the environment variable

Add the mapping to your `.env` file as a JSON object:

```env
SEARCH_SOURCE_OVERRIDES={"<group_chat_id>": "<source_chat_id>"}
```

Example — when `/ask` is used in group `-1004233113745`, search against source chat `1002008115936`:

```env
SEARCH_SOURCE_OVERRIDES={"-1004233113745": "1002008115936"}
```

Multiple overrides:

```env
SEARCH_SOURCE_OVERRIDES={"-1004233113745": "1002008115936", "-1001234567890": "1009876543210"}
```

### Chat ID format

The bot receives chat IDs in **Bot API format** (negative, with `-100` prefix for supergroups). The scraper may use **Telethon format** (positive, no prefix).

The override parser handles this automatically: if you provide a positive key, it converts it to Bot API format by prepending `-100`. For example, Telethon ID `4233113745` becomes Bot API ID `-1004233113745`. Source values (the right side) are stored as-is since they match the `chat_id` column in the `messages` table.

### Verifying the override works

After restarting the bot, check the log output at startup:

```
SEARCH_SOURCE_OVERRIDES = {-1004233113745: 1002008115936}
```

When `/ask` is used in the overridden group, the debug log shows:

```
/ask: chat_id=-1004233113745, search_chat_id=1002008115936, override_hit=True
```

---

## 5. Adding a new onboarding step

The onboarding flow runs when a user first sends `/start` in a DM. It currently collects two preferences: university and language. This guide walks through adding a third step (using timezone as an example).

### The onboarding flow

```
/start → select university → select language → onboarding complete
```

Each step follows the same pattern:
1. Show an inline keyboard with options
2. User taps a button
3. A callback handler saves the selection to the `user_preferences` table
4. The next step's keyboard is shown

### Step 1: Add a database column

Create a numbered migration file following the existing convention (e.g., `sql/011_add_timezone.sql`):

```sql
ALTER TABLE user_preferences ADD COLUMN timezone VARCHAR DEFAULT 'UTC';
```

### Step 2: Add UI strings

In `src/services/language.py`, add strings for the new step:

```python
"ru": {
    # ... existing ...
    "choose_timezone": "Выбери свой часовой пояс:",
    "timezone_updated": "Часовой пояс установлен: {timezone}",
},
"kk": {
    # ... existing ...
    "choose_timezone": "Уақыт белдеуін таңдаңыз:",
    "timezone_updated": "Уақыт белдеуі орнатылды: {timezone}",
},
"en": {
    # ... existing ...
    "choose_timezone": "Choose your timezone:",
    "timezone_updated": "Timezone set to: {timezone}",
},
```

### Step 3: Create the keyboard builder

In `src/services/onboarding_options.py`:

```python
ONBOARD_TIMEZONE_CALLBACK_PREFIX = "onboard:timezone:"

def create_timezone_keyboard() -> InlineKeyboardMarkup:
    timezones = [("UTC+5", "Aqtau"), ("UTC+6", "Almaty/Astana")]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{label} ({tz})", callback_data=f"{ONBOARD_TIMEZONE_CALLBACK_PREFIX}{tz}")
         for tz, label in timezones]
    ])
```

### Step 4: Create the callback handler

In `src/handlers/onboarding.py`:

```python
async def timezone_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle onboarding timezone selection."""
    query = update.callback_query
    await query.answer()

    selected_tz = query.data.removeprefix(ONBOARD_TIMEZONE_CALLBACK_PREFIX)
    try:
        save_user_timezone(query.from_user.id, selected_tz)
    except Exception as e:
        fallback_language = resolve_ui_language(None, telegram_language_code=query.from_user.language_code)
        logger.error("Error saving user timezone: %s", e)
        await query.edit_message_text(get_string(fallback_language, "error"))
        return

    preferences = get_user_preferences(query.from_user.id)
    ui_language = resolve_ui_language(
        preferences.get("language") if preferences else None,
        telegram_language_code=query.from_user.language_code,
    )
    await query.edit_message_text(get_string(ui_language, "timezone_updated", timezone=selected_tz))
```

### Step 5: Add the save function

In `src/services/user_preferences.py`:

```python
def save_user_timezone(user_id: int, timezone: str) -> dict[str, Any]:
    result = (
        supabase.table("user_preferences")
        .upsert(
            {"user_id": user_id, "timezone": timezone.strip()},
            on_conflict="user_id",
        )
        .execute()
    )
    if result.data:
        return result.data[0]
    return get_user_preferences(user_id) or {"user_id": user_id, "timezone": timezone}
```

### Step 6: Register the callback handler

In `main.py`:

```python
from src.handlers.onboarding import timezone_callback_handler

app.add_handler(CallbackQueryHandler(timezone_callback_handler, pattern=r"^onboard:timezone:"))
```

### Step 7: Wire into the /start flow

In `src/handlers/onboarding.py`, update `language_callback_handler()` to show the timezone step after language is saved, instead of completing onboarding immediately.

**Important:** The `onboarded_at` timestamp is currently set inside `save_user_language()`. If your new step comes after language selection, move the `onboarded_at` write from `save_user_language()` to the new final step's save function. Otherwise users will be marked as onboarded before completing all steps.

```python
# Replace the final confirmation message with:
await query.edit_message_text(
    f"{get_string(normalized_language, 'language_updated', language_label=get_language_label(normalized_language))}\n\n"
    f"{get_string(normalized_language, 'choose_timezone')}",
    reply_markup=create_timezone_keyboard(),
)
```

### Checklist

- [ ] Database migration for the new column
- [ ] UI strings in `src/services/language.py` (all 3 languages)
- [ ] Keyboard builder in `src/services/onboarding_options.py`
- [ ] Callback handler in `src/handlers/onboarding.py`
- [ ] Save function in `src/services/user_preferences.py`
- [ ] `CallbackQueryHandler` registered in `main.py`
- [ ] Previous onboarding step updated to show the new keyboard
