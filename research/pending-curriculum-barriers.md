# Remaining pending curriculum evidence

Bounded pass on 2026-10-10 inspected the six program seeds still marked `curriculum_status=pending`. No pending curriculum was promoted by this pass. Access failure does not establish program absence or discontinuation. Previously verified identity evidence remains separate from unavailable curriculum evidence.

| Program | Barrier and exact available locator | Review in this pass |
| --- | --- | --- |
| Gonzaga — AI in Engineering and Applied Science minor | `https://www.gonzaga.edu/robots.txt` returned HTTP 403. The minor source is `https://www.gonzaga.edu/school-of-engineering-applied-science/degrees-and-programs/electrical-computer-engineering/ece-tech-minors/ai-minor`. | Safe fetcher stopped at robots; no minor content fetched. |
| Michigan — Human-Centered Artificial Intelligence minor | `https://www.si.umich.edu/programs/undergraduate-minors/human-centered-artificial-intelligence` returned HTTP 403. | Safe fetcher stopped; no alternative source route attempted. |
| Stony Brook — CS Artificial Intelligence and Data Science specialization | Current official route `https://www.stonybrook.edu/catalog/undergraduate/program/computer-science-bs/` redirects into a catalog service whose `https://catalog.stonybrook.edu/robots.txt` request fails TLS issuer verification. | Existing failure retained; not retried. Fall 2024 source remains historical. Main university robots policy is valid; this is a catalog-host transport/trust failure, not a demonstrated publisher denial. |
| UC Merced — Artificial Intelligence BS | Prior adapter notes report catalog HTTP 403. Identity source: `https://www.ucmerced.edu/majors-and-minors/artificial-intelligence-bs`. The exact failed catalog URL was not retained in the reviewed seed/adapter notes. | Existing denial retained; not retried or replaced with a guessed URL. |
| UC Merced — CSE Artificial Intelligence Emphasis | Prior adapter notes report catalog HTTP 403. Identity source: `https://admissions.ucmerced.edu/academics/majors-minors`. The exact failed catalog URL was not retained in the reviewed seed/adapter notes. | Existing denial retained; not retried or replaced with a guessed URL. |
| Furman — Artificial Intelligence BS | `https://www.furman.edu/academics/majors-minors-programs/artificial-intelligence-major/` was password protected in the previous source inspection. | Existing gate retained; not retried. Public directory confirms identity only. |

No protected source was accessed through another route, TLS verification was not disabled, and no access restriction was interpreted as a negative program finding. Future improvements require newly accessible or independently authoritative public requirements, or an explicitly reviewed change in the recorded access condition.

## Public evidence found after the bounded pass

On2026-10-10, Michigan’s independently public, officially linked UMSI handbook and published course spreadsheet were read without authentication or permission changes. The handbook was exported read-only from its anyone-with-link document; the visible course-table iframe fetched successfully through the robots-aware transport. Michigan now has25 courses,18 requirement/policy nodes and a partial inventory, with exact remaining local-policy/registration gaps in its adapter notes. The main-page default HTTP403 persists. The five other pending inventories are unchanged by this update. The table above is the historical bounded-pass record, not the current status for Michigan.

## Current pending follow-up — 2026-10-11

Five inventories still lack current requirements. Independent public evidence has narrowed the precise boundaries:

- Gonzaga’s separately indexed [academic-catalog entry](https://catalog.gonzaga.edu/undergraduate/engineering-applied-science/ai-in-engineering/) presented a JavaScript/robot-verification page in the ordinary reader. Indexed identity text is not treated as the course inventory.
- Stony Brook’s current catalog service likewise presented verification content in the ordinary reader. The local safe-fetch TLS issuer failure remains a separate recorded condition; neither check was bypassed. The Fall2024 requirements remain historical.
- UC Merced’s official CSE page linked the exact current catalog root, https://catalog.ucmerced.edu/, which returned403. This supplies the previously missing failed locator. Independently public AI BS overview text yielded three program aims and an illustrative career pathway; the School of Engineering supplied six outcomes explicitly scoped to the host CSE program. Neither source supplied current AI BS or emphasis requirements, and neither record was promoted.
- Furman’s listed AI major detail page remains password protected. A separate analytics catalog lead does not establish AI BS requirements; no different credential’s curriculum was imported.

Michigan is no longer pending: its current handbook/course-table inventory is partial, with home-college policies and enrollment/topic details still under review. Counts and requirement-node details in earlier sections above are historical snapshots. No program launch date was inferred from the age of a search hit or these access observations.

### Additional confirmed program — 2026-10-11

The separate Michigan Engineering Artificial Intelligence minor is now confirmed by an independently public Engineering news report, updated April9,2026. Its detailed curriculum is pending: the department entry and indexed committee proposal were unavailable, and no current requirements were inferred from the news. This adds a sixth pending inventory, rather than changing the five original unresolved records. It is not the UMSI Human-Centered AI minor. See its dedicated adapter notes.

The specific Michigan CSE [Artificial Intelligence Minor page](https://cse.engin.umich.edu/academics/undergraduate/minors/artificial-intelligence-minor/) was newly discovered and attempted on 11 October 2026. The public reader returned 403. This is now the precise unverified curriculum target; discovery of its URL and search snippet does not resolve the pending inventory.


### Seventh pending inventory: announced UIC concentration

The [UIC Engineering announcement of April 1, 2026](https://engineering.uic.edu/news-stories/uic-engineering-launches-ai-curriculum-initiatives/) introduces a formal AI concentration for incoming CS students, with planned Fall 2026 availability. It describes four AI technical electives among six overall technical electives, but the inspected current BS Computer Science catalog does not identify the concentration or its approved pool. `uic-cs-ai-concentration` therefore remains **announced**, with curriculum pending and first-offered date unknown. The calendar passing the proposed term is not implementation evidence. See [the adapter notes](../atlas/adapters/uic-cs-ai-concentration/NOTES.md).

As of the 142-program candidate, seven inventories are pending: Gonzaga, Stony Brook, the two UC Merced programs, Furman, the separate Michigan Engineering AI minor, and this UIC concentration. Michigan UMSI's Human-Centered AI minor is partial and is not in that count. Earlier tables above are historical access observations; they should not be read as the current status list.
