# AI Program Atlas

A source-backed research database and static comparison site for undergraduate programs with **AI** or **Artificial Intelligence** in their official title. Standalone degrees, additional majors, minors and concentrations are separate types.

**Coverage is in progress.** The target is the 2027 U.S. News top 100 National Universities and top 100 National Liberal Arts Colleges, separately, including ties. The site reports verified cohort membership and inspection status; pending institutions are never treated as having no program.

## Local workflow

```sh
uv sync --frozen
uv run atlas init
uv run atlas ingest
uv run atlas build --base-path /ai-program-atlas/
uv run pytest
uv run python -m http.server 8000 --directory dist
```

For local root preview, build with `--base-path /`. For Pages-like testing, serve the parent directory containing an `ai-program-atlas/` build. All source adapters can be rerun with `uv run atlas scrape`; fetched material lives in ignored `.cache/` and is never published. Extraction candidates and source changes are queued for review before curated records change. See [architecture](docs/ARCHITECTURE.md), [research plan](PLAN.md), and [data contract](docs/CONTRACT.md).

The public records contain curated factual metadata, original summaries and citations. They do not reproduce full catalogs or CSRankings data. CSRankings values are **not imported** pending reuse permission; missing values do not indicate quality. No ranking here measures undergraduate teaching quality.
