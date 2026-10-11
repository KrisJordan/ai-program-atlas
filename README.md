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

`data/atlas.sqlite` is the maintained research database. Migrations live in `atlas/migrations/`; reviewed factual inputs in `data/programs/`, `data/families/`, `data/cohort.json` and `data/surveys/` reconstruct the public snapshot. The database also preserves revisions, refresh runs, source hashes, extraction candidates and manual overrides. Revision payloads use lossless zlib compression; `atlas.db.revision_record(row)` decodes and verifies a row selected from `program_revisions`. Current canonical snapshots also use lossless zlib compression; `atlas.db.program_record(row)` decodes a row selected from `programs` and verifies its hash. Current relational facts remain directly queryable. Use `--db /tmp/atlas.sqlite` before a subcommand to test a fresh database without altering the maintained copy. Builds read SQLite and make no network requests.

Requirement groups and course links use SQLite composite primary keys without redundant rowid indexes. After large imports or storage migrations, `uv run atlas compact` reclaims unused pages; it does not remove research history or corrections. See [storage validation](research/sqlite-storage-layout.md).

For a local preview:

```sh
uv run atlas build --base-path / --output var/preview
uv run python -m http.server 8000 --directory var/preview
```

For Pages-style paths, build to `var/site/ai-program-atlas` using the default base path, serve `var/site`, and visit `/ai-program-atlas/`. Direct details, reload, back/forward, and copied comparison URLs work without server routing rules. Basic program content works without JavaScript.

The homepage groups records by their documented National University or National Liberal Arts College ranking category. Each group has independent Majors, Concentrations and Minors tabs; Majors includes distinctly labeled additional majors. Major award filters use verified BS/BSE/BA mappings and retain Other/unspecified records. Exact source labels remain visible. `path_nu` / `path_lac` and `award_nu` / `award_lac` preserve these choices in shared URLs, alongside existing search and comparison state. For example, [National University BSE majors](https://krisjordan.github.io/ai-program-atlas/?cohort=National+Universities&path_nu=majors&award_nu=BSE).

Curriculum profiles default to the fixed mapped required set. Elective and required-choice pools are separate, with source-stated selection quantities beside their evidence. Counts use distinct course records, not credits or degree shares; source conditions and unresolved roles remain explicit. `profile=options` selects the option-pool comparison, and browser back/forward restores the view. See the [profile and award contract](docs/CONTRACT.md) for conservative classification and provenance rules.

The [degree correctness audit](docs/DEGREE_AUDIT.md) separately rechecks authoritative sources, identities, requirement roles, credits, course subjects and displayed aggregates. Course taxonomy has explicit reviewed, mixed, unclassified and legacy/unreviewed states. “0 mapped” never proves that a subject is absent from the actual curriculum. Research ledgers live in `research/degree-audit/`; `uv run atlas audit-report` compiles them into `data/degree-audit.json` before ingestion. The maintained database preserves classification rationale and source references relationally. A scraper can propose changed course observations but cannot certify an independent taxonomy review.

## Refresh and review

```sh
uv run atlas scrape                       # All registered program-specific adapters
uv run atlas scrape cmu-bs-ai penn-bse-ai  # Selected adapters
uv run atlas candidates
uv run atlas review 1                     # Compare an observed subset to reviewed fields
uv run atlas status
uv run atlas compact                      # Reclaim unused pages; retain facts and history
```

Refreshes respect robots, bounded retries, Retry-After, per-host pacing, content limits and cache TTL. Crawl intervals up to five minutes are honored in waits of at most 30 seconds each; longer intervals are deferred. A 120-second policy therefore slows retrieval instead of being treated as a denial. No 401/403/paywall bypass is attempted. A source may be manually inspectable while rejecting the unattended fetcher; record this limitation. Raw HTML stays in ignored `.cache/`, outside Git and the public build. Nonzero refresh exit status means at least one source needs review; successful observations are retained.

A successful parse creates a candidate, not permission to erase researched fields. Review the official source and adapter `NOTES.md`, update the curated JSON, then ingest. Failed or partial runs never delete existing facts. Repeated identical observations do not duplicate candidates. Source-body changes are recorded even when extracted identity fields are unchanged.

Evidence-backed editorial overrides survive reimports:

```sh
uv run atlas override PROGRAM_ID overview '"Reviewed summary"' \
  --reason 'Verified correction' --evidence-url 'https://official.example.edu/program'
```

Structural curriculum corrections belong in reviewed JSON; scraping does not overwrite it. Shared family requirements are stored once and resolved through reviewed variant bindings. Explicit additions, replacements and exclusions preserve differences; see [program families](docs/PROGRAM_FAMILIES.md). See [data contract](docs/CONTRACT.md), [architecture](docs/ARCHITECTURE.md), [research skill](.agents/skills/atlas-research/SKILL.md), and [refresh skill](.agents/skills/atlas-refresh/SKILL.md).

## Publication and data rights

GitHub Actions validates a fresh database reconstruction, runs unit/integration and required Chromium browser tests, then ingests current reviewed inputs into a copy of the maintained database before building and deploying GitHub Pages. This publication copy preserves evidence-backed manual corrections and research history; CI never overwrites the committed database. Public artifacts contain factual metadata, original summaries and citations. They exclude raw catalogs, credentials and private user context. Public course sites and syllabus examples are links with term notes, not redistributed documents.

CSRankings research context is imported for the five AI fields and aggregate, using the pinned September 28, 2026 snapshot and the project's 2016–2025 U.S. window. All eligible U.S. institutions are ranked before joining this roster. The original upstream JavaScript independently reproduced all 961 observed scores and ranks. Owner-confirmed educational permission, attribution, source hashes, field membership and distinct missingness states are recorded. Publication measures and U.S. News ranks are not undergraduate teaching-quality scores. See [methodology and permission](research/csrankings.md) and [reproducible importer](research/csrankings-integration.md).

Robots matching, pacing and conservative access boundaries are documented in [HTTP policy](docs/HTTP_POLICY.md).
