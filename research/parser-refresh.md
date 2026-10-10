# Discovery parser refresh — 2026-10-10

The first live run produced 47 identity parsing failures after successful source fetches. Replaying those ignored local cache bodies after these repairs resolved **46 of 47**. This is cached parser verification, not a new network fetch or a reviewed-fact update. The coordinator will run the normal fetch/snapshot/candidate pipeline separately.

## Causes and fixes

- Courseleaf and news pages place legitimate program H1s inside content headers. Retain those headers while removing global navigation, sidebars, hidden content and unrelated global headers.
- Cornell's program hero and Miami/Northeastern catalog titles sit outside the selected main content root. Source-specific reviewed scopes now include those exact identity blocks.
- Northeastern's combined-major directory omits the award in its visible link labels. Accept the observed Boston title spelling and inherit BS only from the heading immediately preceding that entry's list. Sidebar links are not evidence.
- Buffalo lists degree/minor identities as plain list entries; Case lists AI BA/BS pathways under a bold list label. Read individual leaf entries, without mixing identities and awards from sibling or nested entries.
- Layout wrappers separated Notre Dame's program heading from its description. Heading context now follows DOM order across wrappers and stops at the next heading.
- Stevens publishes its award in a separate Degree field within the program hero. A reviewed hero scope links it to the program title.
- Maryland describes the BA in a specific pathway paragraph. Only the sentence containing the expected program identity may provide its award.
- Emory uses the explicit heading `AI Minor`; the adapter records that source alias. Punctuated degree abbreviations normalize without inventing degree types.

The shared helper has no general prose/body fallback. Explicit scopes remain subject to access-page, password, navigation and hidden-content rejection. Identity observations contain only ID, title, award and kind; no seed fixture, launch date, curriculum or freshness claim is replayed.

## Validation and unresolved work

`tests/test_discovery_adapters.py`: **95 passed**, including 13 additional regression cases for real layout structures and false-positive boundaries. Broader cached replay of all adapters using the shared helper found 74 successes, one unresolved parse and three sources without cached bodies. Raw HTML was not committed.

The unresolved parse is NJIT's Business with AI catalog page: the cached page explicitly names the program and curriculum but does not state a BS award in visible content. The parser continues to reject this observation. A reviewed official source containing both identity and award is needed; a URL ending in `-bs` is insufficient evidence.

The original network run also reported access restrictions for Gonzaga (robots 403), two UC Merced sources (robots 403), and Michigan (target HTTP 403). Parser repairs do not bypass or resolve these restrictions. These fetch failures are separate from the 47 valid-HTTP parse failures. Final survey adapters using a different helper are outside this patch's cached replay count.
