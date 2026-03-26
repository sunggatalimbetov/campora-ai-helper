# Feature: Admin Commands for Group Management

## Problem

Group admins have no control over the bot's behavior in their group. They can't adjust rate limits, disable the bot during busy periods, or configure any settings without modifying environment variables and restarting.

## Solution

Add admin-only commands that allow group administrators to configure the bot's behavior per-group.

## Technical Design

### Commands

| Command | Description |
|---------|-------------|
| `/settings` | Show current group settings |
| `/toggle` | Enable/disable bot responses in this group |
| `/setlimit <n>` | Set max queries per user per hour (default 10) |
| `/quiet <start> <end>` | Set quiet hours (e.g., `/quiet 23:00 07:00`) |

### Database: `bot_group_settings` Table

```sql
CREATE TABLE bot_group_settings (
    chat_id BIGINT PRIMARY KEY,
    enabled BOOLEAN DEFAULT TRUE,
    rate_limit_per_hour INTEGER DEFAULT 10,
    quiet_start TIME DEFAULT NULL,
    quiet_end TIME DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Admin Check

Use Telegram API to verify the user is an admin:

```python
async def is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user is an admin of the current group."""
    if update.effective_chat.type == "private":
        return False
    member = await context.bot.get_chat_member(
        update.effective_chat.id, update.effective_user.id
    )
    return member.status in ("administrator", "creator")
```

### Settings Service

Create `src/services/group_settings.py`:

```python
from src.services.message_search._clients import supabase


def get_group_settings(chat_id: int) -> dict:
    """Get settings for a group, or defaults if none set."""
    result = supabase.table("bot_group_settings").select("*").eq("chat_id", chat_id).execute()
    if result.data:
        return result.data[0]
    return {
        "chat_id": chat_id,
        "enabled": True,
        "rate_limit_per_hour": 10,
        "quiet_start": None,
        "quiet_end": None,
    }


def update_group_settings(chat_id: int, **kwargs) -> None:
    """Update group settings (upsert)."""
    supabase.table("bot_group_settings").upsert(
        {"chat_id": chat_id, **kwargs}
    ).execute()
```

### Integration with Other Features

- **Rate Limiter** (feature 12): Read `rate_limit_per_hour` from group settings instead of global env var
- **Relevance Filter** (feature 08): Check `enabled` before processing
- **Quiet Hours**: Check time before responding

```python
# In group message handler, before processing:
settings = get_group_settings(chat_id)

if not settings["enabled"]:
    return

if is_quiet_hours(settings["quiet_start"], settings["quiet_end"]):
    return
```

## Files to Change

- `sql/` — migration for `bot_group_settings` table
- Create `src/services/group_settings.py` — settings CRUD
- Create `src/handlers/admin.py` — admin command handlers
- `main.py` — register new command handlers
- `src/services/rate_limiter.py` — read per-group limits from settings
- `src/handlers/commands.py` — check `enabled` and quiet hours before responding

## Implementation Checklist

- [ ] Create `bot_group_settings` table migration
- [ ] Create `src/services/group_settings.py`
- [ ] Create `src/handlers/admin.py` with admin check + commands
- [ ] Register `/settings`, `/toggle`, `/setlimit`, `/quiet` in `main.py`
- [ ] Integrate `enabled` check in group message handler
- [ ] Integrate quiet hours check
- [ ] Connect rate limiter to per-group settings
- [ ] Test: non-admin runs `/toggle` → rejected
- [ ] Test: admin runs `/toggle` → bot disables/enables
- [ ] Test: `/setlimit 5` → rate limit changes for that group

## Status

Planned
