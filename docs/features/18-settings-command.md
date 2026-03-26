# Feature: /settings Command

## Problem

After onboarding, users have no way to change their selected group or language preference without restarting the bot. Preferences should be easy to update at any time.

## Solution

Add a `/settings` command that shows the user's current preferences and lets them change group or language via inline buttons.

## Technical Design

### Flow

User sends `/settings` → bot replies:

```
⚙️ Настройки

Университет: UNIME
Язык: Русский

Что хочешь изменить?
```

Two inline buttons: `[Университет]` `[Язык]`

Pressing "Университет" → same group selection buttons as onboarding.
Pressing "Язык" → same language buttons as onboarding.

After selection → update the preference and confirm:

```
✅ Университет изменён на NU
```

### Handler

```python
async def settings_command(update, context):
    user_id = update.effective_user.id
    prefs = get_user_preferences(user_id)

    if not prefs:
        await update.message.reply_text("Сначала пройди настройку: /start")
        return

    group = prefs.get("selected_group", "все").upper()
    lang_map = {"ru": "Русский", "kk": "Қазақша", "en": "English"}
    lang = lang_map.get(prefs.get("language", "ru"), "Русский")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Университет", callback_data="settings:group"),
         InlineKeyboardButton("Язык", callback_data="settings:lang")]
    ])
    await update.message.reply_text(
        f"⚙️ Настройки\n\nУниверситет: {group}\nЯзык: {lang}\n\nЧто хочешь изменить?",
        reply_markup=keyboard,
    )
```

### Callback Handlers

Reuse the same inline keyboards from the onboarding flow (feature 17). The callbacks update user_preferences and confirm the change.

```python
async def settings_group_callback(update, context):
    # Show group selection buttons (same as onboarding)
    ...

async def settings_lang_callback(update, context):
    # Show language selection buttons (same as onboarding)
    ...
```

### UI Messages

All `/settings` UI messages should respect the user's current language preference.

## Files to Change

- `src/handlers/onboarding.py` — add settings command + callbacks (or create separate `settings.py`)
- `main.py` — register `/settings` command handler
- Reuse `src/services/user_preferences.py` from feature 17

## Implementation Checklist

- [ ] Add `settings_command` handler
- [ ] Add settings callback handlers for group and language changes
- [ ] Register `/settings` in `main.py`
- [ ] Update `/help` text to mention `/settings`
- [ ] Test: change group → search results scoped to new group
- [ ] Test: change language → UI messages in new language

## Dependencies

- Feature 17 (Onboarding Flow) — requires `user_preferences` table and preference service

## Status

Planned
