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
