---
name: atlas-refresh
description: Rerun AI Program Atlas source adapters, review changed evidence, preserve corrections, and verify a static publication build.
---

Use the maintained SQLite database and `uv` commands in README.md. `atlas scrape` fetches permitted pages with robots, pacing, cache, bounded retries and size limits. A 401/403, robots restriction, paywall or password is an access limit, not a request to find a bypass. Record the blocker and continue independent sources.

Scrapes create observations/candidates and source hashes; they do not replace curated records. Use `atlas candidates` and compare the parsed subset to the current JSON and source. Review additions/removals and changed choice rules; partial extraction must not erase earlier researched fields. Update reviewed JSON only after evidence review, then ingest. Keep manual corrections in the overrides table with a reason and evidence; reimports preserve them.

Use a temporary database for clean reconstruction checks. Compare deterministic exports, run unit/integration and real browser tests, and check base-path navigation, comparison reload/back/forward, empty states and mobile. Build outputs have no runtime server or private data. Keep source cache and credentials untracked. Publishing is limited to the dedicated authorized repository; verify the remote commit, CI and Pages URL before reporting deployment complete. Preserve PLAN.md's unresolved cohort/data limitations after deployment.
