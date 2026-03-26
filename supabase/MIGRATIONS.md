# Reconstructed Migration History

This repository was missing its timestamped `supabase/migrations` files even
though the remote Supabase project already had migration history recorded.

The migration files were reconstructed from:

- the `sql/` snapshots in this repo
- git history
- documented migration names in `docs/history/02-hybrid-search.md`

Two historical versions from the remote project could not be recovered exactly:

- `20260216020000`
- `20260220120000`

Those are represented as no-op placeholder migrations so local migration
tracking can reconcile with the remote database. They exist for CLI history
compatibility and should be replaced only if the original SQL is recovered.
