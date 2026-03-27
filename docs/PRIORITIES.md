# Implementation Priorities

Canonical execution order for `campora-ai-helper`.

This file is the source of truth for what we should work on next. Feature specs live in [docs/features](docs/features); this file decides sequencing.

## Current State

Recently completed or effectively unblocked:

| ID | Feature | Status |
|---|---|---|
| 13 | [Group-scoped search](docs/features/13-group-scoped-search.md) | Implemented (PR #11) |
| 19 | [Batch reply fetching](docs/features/19-batch-reply-fetching.md) | Implemented (PR #12) |
| 20 | [Thread-grouped context](docs/features/20-thread-grouped-context.md) | Implemented (PR #15) |
| 14 | [Language-aware responses](docs/features/14-language-aware-responses.md) | Implemented (PRs #18-20) — full localized UI with /language command |
| 24 | [Better no-results](docs/features/24-better-no-results.md) | Implemented — localized no-results messages shipped as part of language PRs |
| — | Group mention handler | Implemented (PR #21) |
| 21 | [Similarity threshold filter](docs/features/21-similarity-threshold-filter.md) | Implemented — filters results below 0.45 semantic similarity |

Operational work recently handled:

- Supabase migration tracking repaired (PR #14)
- Legacy Supabase RPC overloads removed (PR #16)
- Message embedding index path validated in production
- Rename from Vectir AI to Campora AI (PR #22, merged)

## Now

These are the next features to implement in order.

| Order | ID | Feature | Why now |
|---|---|---|---|
| 1 | 22 | [Trim conversation history](docs/features/22-trim-conversation-history.md) | Keeps prompts tighter and reduces irrelevant conversational carry-over |
| 2 | 25 | [Message length guard](docs/features/25-message-length-guard.md) | Prevents Telegram send failures once answer quality improves |

## Next

Important improvements after the current block.

| Order | ID | Feature | Why next |
|---|---|---|---|
| 3 | 09 | [Shorter group answers](docs/features/09-shorter-group-answers.md) | Better fit for Telegram group dynamics |
| 4 | 23 | [Smarter references](docs/features/23-smarter-references.md) | Improves trust and answer grounding |
| 5 | 11 | [Typing indicator](docs/features/11-typing-indicator.md) | Low-effort improvement to responsiveness |
| 6 | 17 | [Onboarding flow](docs/features/17-onboarding-flow.md) | Helps first-time users ask the right kind of questions |
| 7 | 18 | [Settings command](docs/features/18-settings-command.md) | Natural companion to onboarding and DM UX |

## Later

Valuable, but either bigger or less urgent for the current launch path.

| ID | Feature | Why later |
|---|---|---|
| 07 | [Welcome message](docs/features/07-welcome-message.md) | Some of this is already partially covered by `/start`; should be revisited together with onboarding |
| 08 | [Relevance filter](docs/features/08-relevance-filter.md) | Likely overlaps with 21 and may need consolidation before implementation |
| 10 | [Reply threading](docs/features/10-reply-threading.md) | Partially addressed by 19 and 20; may need reframing |
| 12 | [Rate limiting](docs/features/12-rate-limiting.md) | More important once usage grows |
| 15 | [Admin commands](docs/features/15-admin-commands.md) | Operationally useful, but not blocking answer quality |
| 01 | [Question generation indexing](docs/features/01-question-generation-indexing.md) | Bigger retrieval investment after current quality fixes settle |
| 03 | [Keyword extraction & two-stage retrieval](docs/features/03-keyword-extraction-two-stage-retrieval.md) | More invasive search work than current launch path needs |
| 04 | [Multi-university scaling](docs/features/04-multi-university-scaling.md) | Expansion problem, not current product bottleneck |
| 16 | [Inline mode](docs/features/16-inline-mode.md) | Nice-to-have interface expansion |

## Notes

- Meta queries such as "What can you do?" should eventually bypass retrieval and return bot help directly.
- DB-sensitive work should be validated in Supabase before merge.
- If a feature is implemented, move its spec to [docs/history](docs/history) once the implementation is fully merged and stable.
