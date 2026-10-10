# AI Program Atlas

[Explore the published atlas](https://krisjordan.github.io/ai-program-atlas/) · [Coverage](https://krisjordan.github.io/ai-program-atlas/coverage/) · [Methodology](https://krisjordan.github.io/ai-program-atlas/methodology/)

A maintained relational SQLite research database and static comparison site for undergraduate programs with **AI** or **Artificial Intelligence** in their official title. Degrees, additional majors, minors and formal concentrations/tracks are distinct. The site has accessible Carolina-blue/navy navigation, filters, direct program pages, query-string comparison permalinks, course profiles, inferred outcome-theme comparisons and source provenance. Evidence-backed program families group related AI + discipline degrees while preserving every concrete award and its own comparison URL.

**Research coverage is incomplete.** The target is the 2027 U.S. News top 100 National Universities and top 100 National Liberal Arts Colleges, separately, including ties. The current roster includes secondary-sourced ranks and an incomplete liberal arts enumeration. An unlisted program is never treated as absent. Identity verification, curriculum extraction and institutional search completeness are separate facts. See [PLAN.md](PLAN.md) for the current research checkpoint and remaining work.

## Reproduce the site

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). On the original Studio workspace, an isolated uv bootstrap is also available at `.tooling/bin/uv` (not committed); use it in place of `uv` if uv is not on PATH.

```sh
uv sync --frozen
uv run atlas init
uv run atlas ingest
uv run atlas check
uv run atlas build --base-path /ai-program-atlas/
uv run playwright install chromium
ATLAS_REQUIRE_BROWSER=1 uv run pytest -q
```

`data/atlas.sqlite` is the maintained research database. Migrations live in `atlas/migrations/`; reviewed factual inputs in `data/programs/`, `data/families/`, `data/cohort.json` and `data/surveys/` reconstruct the public snapshot. The database also preserves revisions, refresh runs, source hashes, extraction candidates and manual overrides. Use `--db /tmp/atlas.sqlite` before a subcommand to test a fresh database without altering the maintained copy. Builds read SQLite and make no network requests.

For a local preview:

```sh
uv run atlas build --base-path / --output var/preview
uv run python -m http.server 8000 --directory var/preview
```

For Pages-style paths, build to `var/site/ai-program-atlas` using the default base path, serve `var/site`, and visit `/ai-program-atlas/`. Direct details, reload, back/forward, and copied comparison URLs work without server routing rules. Basic program content works without JavaScript.

## Refresh and review

```sh
uv run atlas scrape                       # All registered program-specific adapters
uv run atlas scrape cmu-bs-ai penn-bse-ai  # Selected adapters
uv run atlas candidates
uv run atlas review 1                     # Compare an observed subset to reviewed fields
uv run atlas status
```

Refreshes respect robots, bounded retries, Retry-After, per-host pacing, content limits and cache TTL. No 401/403/paywall bypass is attempted. A source may be manually inspectable while rejecting the unattended fetcher; record this limitation. Raw HTML stays in ignored `.cache/`, outside Git and the public build. Nonzero refresh exit status means at least one source needs review; successful observations are retained.

A successful parse creates a candidate, not permission to erase researched fields. Review the official source and adapter `NOTES.md`, update the curated JSON, then ingest. Failed or partial runs never delete existing facts. Repeated identical observations do not duplicate candidates. Source-body changes are recorded even when extracted identity fields are unchanged.

Evidence-backed editorial overrides survive reimports:

```sh
uv run atlas override PROGRAM_ID overview '"Reviewed summary"' \
  --reason 'Verified correction' --evidence-url 'https://official.example.edu/program'
```

Structural curriculum corrections belong in reviewed JSON; scraping does not overwrite it. Shared family requirements are stored once and resolved through reviewed variant bindings. Explicit additions, replacements and exclusions preserve differences; see [program families](docs/PROGRAM_FAMILIES.md). See [data contract](docs/CONTRACT.md), [architecture](docs/ARCHITECTURE.md), [research skill](.agents/skills/atlas-research/SKILL.md), and [refresh skill](.agents/skills/atlas-refresh/SKILL.md).

## Publication and data rights

GitHub Actions validates a fresh database reconstruction, runs unit/integration and required Chromium browser tests, then ingests current reviewed inputs into a copy of the maintained database before building and deploying GitHub Pages. This publication copy preserves evidence-backed manual corrections and research history; CI never overwrites the committed database. Public artifacts contain factual metadata, original summaries and citations. They exclude raw catalogs, credentials and private user context. Public course sites and syllabus examples are links with term notes, not redistributed documents.

CSRankings numeric values are **not imported** pending reuse permission. The project records field membership, proposed year window, U.S. filter, snapshot and computation method; links lead to the original source. Missing values do not indicate quality. Publication measures and U.S. News cohort ranks are not undergraduate teaching-quality scores. See [CSRankings research note](research/csrankings.md).
