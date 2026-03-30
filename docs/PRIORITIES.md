# Implementation Priorities

Canonical execution order for `campora-ai-helper`.

This file is the source of truth for what we should work on next. Feature specs live in [docs/features](docs/features); this file decides sequencing.

## Current State

All of the following are merged and stable as of 2026-03-30:

| ID | Feature | PR(s) |
|---|---|---|
| — | /optout and /optin privacy commands | #1 |
| — | Message timestamps in search and answers | #2 |
| — | Fix validate feedback type | #3 |
| 13 | [Group-scoped search](history/13-group-scoped-search.md) | #11 |
| 19 | [Batch reply fetching](history/19-batch-reply-fetching.md) | #12 |
| 20 | [Thread-grouped context](history/20-thread-grouped-context.md) | #15 |
| 14 | [Language-aware responses](history/14-language-aware-responses.md) | #18–20 |
| — | Group mention handler | #21 |
| 21 | [Similarity threshold filter](history/21-similarity-threshold-filter.md) | #23 |
| 22 | [Trim conversation history](history/22-trim-conversation-history.md) | #24, #34 |
| 25 | [Message length guard](history/25-message-length-guard.md) | #26 |
| 11 | [Typing indicator](history/11-typing-indicator.md) | #27 |
| 09 | [Shorter group answers](history/09-shorter-group-answers.md) | #28, #30 |
| — | Extract answer utils refactor | #29 |
| 23 | [Smarter references](history/23-smarter-references.md) | #31 |
| 12 | [Rate limiting](history/12-rate-limiting.md) | #32 |
| — | Search source overrides | #33 |
| 17 | [Onboarding flow](history/17-onboarding-flow.md) | #35 |
| 04 | DB-driven university & multi-chat search (infrastructure) | #36 |
| 24 | [Better no-results](history/24-better-no-results.md) | shipped with #18–20 |

Operational work:
- Supabase migration tracking repaired (#14)
- Legacy Supabase RPC overloads removed (#16)
- Rename from Vectir AI to Campora AI (#22)
- README added (#25)

## Now

| Order | ID | Feature | Why now |
|---|---|---|---|
| 1 | 18 | [Settings command](features/18-settings-command.md) | Feature 17 (onboarding) is done — `/settings` is the natural companion for changing university/language after onboarding |

## Next

| Order | ID | Feature | Why next |
|---|---|---|---|
| 2 | 07 | [Welcome message](features/07-welcome-message.md) | Onboarding is done — welcome message should be revisited and aligned with new onboarding flow |
| 4 | 08 | [Relevance filter](features/08-relevance-filter.md) | May overlap with similarity threshold (21); needs review now that 21 is shipped |

## Later

Valuable but not urgent for current launch path.

| ID | Feature | Why later |
|---|---|---|
| 10 | [Reply threading](features/10-reply-threading.md) | Partially addressed by 19 and 20; may need reframing |
| 15 | [Admin commands](features/15-admin-commands.md) | Operationally useful, not blocking quality |
| 16 | [Inline mode](features/16-inline-mode.md) | Nice-to-have interface expansion |

## Notes

- Meta queries such as "What can you do?" should eventually bypass retrieval and return bot help directly.
- DB-sensitive work should be validated in Supabase before merge.
- If a feature is implemented, move its spec to [docs/history](history) once fully merged and stable.
