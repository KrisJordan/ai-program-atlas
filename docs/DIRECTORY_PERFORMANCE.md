# Directory payload audit — 2026-10-11

Evidence snapshot: committed `660706014c2df58d33b62bee8bb09eb5fa7d32de`, reconstructed in an isolated temporary SQLite database. Research working-tree edits were excluded. Both measurements use exactly the same export, base path, build environment and deterministic `gzip.compress(..., mtime=0)` compression. These are file sizes, not an assumption about GitHub Pages transport headers or measured user latency.

| Directory HTML | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Raw bytes | 3,960,081 | 2,296,852 | 42.0% |
| Gzip bytes | 459,473 | 290,326 | 36.8% |

The build-time comparison view previously repeated graph IDs and parent IDs for all 5,282 projected requirement rows, root summaries/source IDs that comparison never rendered, and null selection fields. It now stores an explicit root flag, root selection facts, and every family-local/replacement title, summary, component and source reference. Shared-family definitions and explicit override identifiers remain unchanged because comparison uses them.

No evidence is removed from the public export. Full `data.json` and all 125 static program detail pages are byte-for-byte unchanged for the same input. The root's no-JavaScript directory is unchanged. No runtime fetch or lazy-loading dependency is introduced. Course code/name search text, family and discipline filters, outcome provenance, metadata counts, ranking context and URL/history behavior are retained.

Remaining embedded JSON is 2,099,280 bytes: approximately 1,222,662 in comparison requirement rows, 487,568 in course-inclusive search text and 389,050 in other fields/structure. The remaining local requirement summaries are actively rendered evidence. Interning strings or loading comparison data separately would increase runtime complexity; this audit does not justify that broader rewrite or impose a fixed size budget.

Validation uses the existing strict Chromium suite with mobile/desktop, keyboard family expansion, comparison scroll-region focus, named controls/live status, native no-JavaScript disclosure, catalog search, source links, comparison selection/reload/back/forward and direct detail routes. Projection tests compare every retained real-data root/variant display field, source URL, course search term and metadata count against the full export. This is bounded functional/accessibility verification, not a comprehensive assistive-technology certification.

Result: `ATLAS_REQUIRE_BROWSER=1 ... python -m pytest tests/e2e tests/test_site.py tests/test_directory_payload.py -q` passed **30 tests**, including all **17 Chromium scenarios**, against the isolated committed snapshot plus this frontend change. No tests skipped. Initial sandboxed Chromium launch was denied by macOS; the authorized escalated run passed. Covered real-data mobile/desktop routes reported no document overflow or JavaScript errors.
