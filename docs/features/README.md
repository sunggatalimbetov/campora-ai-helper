# Feature Backlog

Active feature specs for `vectir-ai-helper`.

Completed items should move to [docs/history](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/history). Strategy notes and brainstorming should live in roadmap/backlog docs rather than this folder.

## Current Priorities

### Tier 0 — Launch critical

These directly affect trust, answer quality, or response reliability:

| ID | Feature | Why it matters |
|---|---|---|
| 13 | Group-scoped search | Prevents answers from leaking across groups |
| 19 | Batch reply fetching | Removes N+1 database queries from retrieval |
| 20 | Thread-grouped context | Preserves message/reply structure for the LLM |
| 21 | Similarity threshold filter | Reduces noisy context and hallucination risk |
| 24 | Better no-results | Turns dead ends into recovery paths |
| 25 | Message length guard | Prevents Telegram send failures on long answers |

### Tier 1 — Strong next steps

High-value improvements once Tier 0 is in place:

| ID | Feature |
|---|---|
| 09 | Shorter group answers |
| 14 | Language-aware responses |
| 22 | Trim conversation history |
| 23 | Smarter references |
| 11 | Typing indicator |

### Tier 2 — Product completeness

Helpful for deployment and admin control:

| ID | Feature |
|---|---|
| 07 | Welcome message |
| 12 | Rate limiting |
| 15 | Admin commands |
| 17 | Onboarding flow |
| 18 | Settings command |

### Tier 3 — Bigger bets

Useful, but more invasive or less urgent for launch:

| ID | Feature |
|---|---|
| 01 | Question generation indexing |
| 03 | Keyword extraction & two-stage retrieval |
| 04 | Multi-university scaling |
| 16 | Inline mode |

## Active Specs

| ID | File |
|---|---|
| 01 | [01-question-generation-indexing.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/01-question-generation-indexing.md) |
| 03 | [03-keyword-extraction-two-stage-retrieval.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/03-keyword-extraction-two-stage-retrieval.md) |
| 04 | [04-multi-university-scaling.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/04-multi-university-scaling.md) |
| 07 | [07-welcome-message.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/07-welcome-message.md) |
| 08 | [08-relevance-filter.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/08-relevance-filter.md) |
| 09 | [09-shorter-group-answers.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/09-shorter-group-answers.md) |
| 10 | [10-reply-threading.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/10-reply-threading.md) |
| 11 | [11-typing-indicator.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/11-typing-indicator.md) |
| 12 | [12-rate-limiting.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/12-rate-limiting.md) |
| 13 | [13-group-scoped-search.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/13-group-scoped-search.md) |
| 14 | [14-language-aware-responses.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/14-language-aware-responses.md) |
| 15 | [15-admin-commands.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/15-admin-commands.md) |
| 16 | [16-inline-mode.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/16-inline-mode.md) |
| 17 | [17-onboarding-flow.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/17-onboarding-flow.md) |
| 18 | [18-settings-command.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/18-settings-command.md) |
| 19 | [19-batch-reply-fetching.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/19-batch-reply-fetching.md) |
| 20 | [20-thread-grouped-context.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/20-thread-grouped-context.md) |
| 21 | [21-similarity-threshold-filter.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/21-similarity-threshold-filter.md) |
| 22 | [22-trim-conversation-history.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/22-trim-conversation-history.md) |
| 23 | [23-smarter-references.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/23-smarter-references.md) |
| 24 | [24-better-no-results.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/24-better-no-results.md) |
| 25 | [25-message-length-guard.md](/Users/sunggat/Projects/vectir-ai/vectir-ai-helper/docs/features/25-message-length-guard.md) |
