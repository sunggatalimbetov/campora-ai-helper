# Implementation Priorities

Canonical execution order for `campora-ai-helper`.

This file is the source of truth for what we should work on next. Feature specs live in [docs/features](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features); this file decides sequencing.

## Current State

Recently completed or effectively unblocked:

| ID | Feature | Status |
|---|---|---|
| 13 | [Group-scoped search](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/13-group-scoped-search.md) | Implemented |
| 19 | [Batch reply fetching](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/19-batch-reply-fetching.md) | Implemented |
| 20 | [Thread-grouped context](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/20-thread-grouped-context.md) | Implemented / pending merge if branch still open |

Operational work recently handled:

- Supabase migration tracking repaired
- Legacy Supabase RPC overloads removed
- Message embedding index path validated in production

## Now

These are the next features to implement in order.

| Order | ID | Feature | Why now |
|---|---|---|---|
| 1 | 24 | [Better no-results](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/24-better-no-results.md) | Users are hitting empty or weak retrieval flows today; this is the highest UX pain |
| 2 | 21 | [Similarity threshold filter](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/21-similarity-threshold-filter.md) | Live tests still show noisy retrieval that should be filtered before answer generation |
| 3 | 14 | [Language-aware responses](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/14-language-aware-responses.md) | Core product audience is RU/KZ/EN, so response language matching matters immediately |
| 4 | 22 | [Trim conversation history](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/22-trim-conversation-history.md) | Keeps prompts tighter and reduces irrelevant conversational carry-over |
| 5 | 25 | [Message length guard](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/25-message-length-guard.md) | Prevents Telegram send failures once answer quality improves |

## Next

Important improvements after the current block.

| Order | ID | Feature | Why next |
|---|---|---|---|
| 6 | 09 | [Shorter group answers](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/09-shorter-group-answers.md) | Better fit for Telegram group dynamics |
| 7 | 23 | [Smarter references](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/23-smarter-references.md) | Improves trust and answer grounding |
| 8 | 11 | [Typing indicator](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/11-typing-indicator.md) | Low-effort improvement to responsiveness |
| 9 | 17 | [Onboarding flow](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/17-onboarding-flow.md) | Helps first-time users ask the right kind of questions |
| 10 | 18 | [Settings command](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/18-settings-command.md) | Natural companion to onboarding and DM UX |

## Later

Valuable, but either bigger or less urgent for the current launch path.

| ID | Feature | Why later |
|---|---|---|
| 07 | [Welcome message](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/07-welcome-message.md) | Some of this is already partially covered by `/start`; should be revisited together with onboarding |
| 08 | [Relevance filter](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/08-relevance-filter.md) | Likely overlaps with 21 and may need consolidation before implementation |
| 10 | [Reply threading](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/10-reply-threading.md) | Partially addressed by 19 and 20; may need reframing |
| 12 | [Rate limiting](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/12-rate-limiting.md) | More important once usage grows |
| 15 | [Admin commands](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/15-admin-commands.md) | Operationally useful, but not blocking answer quality |
| 01 | [Question generation indexing](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/01-question-generation-indexing.md) | Bigger retrieval investment after current quality fixes settle |
| 03 | [Keyword extraction & two-stage retrieval](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/03-keyword-extraction-two-stage-retrieval.md) | More invasive search work than current launch path needs |
| 04 | [Multi-university scaling](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/04-multi-university-scaling.md) | Expansion problem, not current product bottleneck |
| 16 | [Inline mode](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/features/16-inline-mode.md) | Nice-to-have interface expansion |

## Notes

- Meta queries such as "What can you do?" should eventually bypass retrieval and return bot help directly.
- DB-sensitive work should be validated in Supabase before merge.
- If a feature is implemented, move its spec to [docs/history](/Users/sunggat/Projects/campora-ai/campora-ai-helper/docs/history) once the implementation is fully merged and stable.
