# CSRankings research context — educational permission confirmed

## Permission and current integration

On October 11, 2026, project owner Kris Jordan confirmed: “We have permission to use csrankings data for this educational project.” The integration relies on that project-specific confirmation. No licensor document or broader redistribution right has been supplied or is claimed. Preserve upstream attribution, license notices, source snapshot and methodology. Numerical integration is now authorized for this educational Atlas and has been implemented and independently checked; the historical hold below no longer describes the current permission state.

The project configuration remains 2016–2025 inclusive, United States, with individually reported `ai`, `vision`, `mlmining`, `nlp`, `inforet` fields and an explicitly defined aggregate. Compute the full eligible U.S. population before joining the Atlas roster. Keep absent, ineligible, no-output and unresolved matches distinct; none means zero educational quality.

The current derived artifact covers 201 listed U.S. institutions across six selections: 961 observed and 245 no-selected-output rows. The 194-institution Atlas roster has 91 reviewed matches and 103 not-listed institutions. Not-listed does not establish doctoral eligibility. See [integration evidence](csrankings-integration.md) and [independent original-JavaScript replay](csrankings-peer-review.md).

## Historical pre-permission research (2026-10-10)

Everything below records the former hold and proposal; it does not describe the current imported snapshot.

Verified 2026-10-10 against the [official FAQ](https://csrankings.org/faq) and pinned [September 28, 2026 source snapshot](https://github.com/emeryberger/CSrankings/commit/5e8a27d68310c728a182b8bb3b6437c39bce0cad). No source dataset or implementation is included in this repository. Public numeric import is held pending permission or qualified reuse review; this is a project limitation, not a claim that every factual citation is prohibited.

## Proposed reproducible configuration

Five fields, separately and in an aggregate: `ai`, `vision`, `mlmining`, `nlp`, `inforet`. Default venues are AAAI/IJCAI; CVPR/ECCV/ICCV; ICLR/ICML/NeurIPS; ACL/EMNLP/NAACL; and SIGIR/WWW. KDD is a separate next-tier toggle, disabled by default; robotics is outside this AI group. Proposed project window: **2016–2025**, ten completed calendar years; geographic filter **us**. This is a project choice, not the site's current default. The current default spans current year minus ten through current year inclusive, and thus includes incomplete 2026.

A future authorized calculation should rank all eligible U.S. institutions first, then join the atlas cohort with reviewed institution aliases. Record snapshot, year bounds, country, venue toggles, crosswalk and rounding. Preserve individual field observations and explicit field membership for the aggregate. Do not average ordinal ranks.

The FAQ describes equal fractional credit across all authors and a geometric aggregation of adjusted field counts plus one. The pinned implementation rounds displayed aggregate values to one decimal before competition ranking. It does not normalize by faculty size. Affiliation reflects the selected snapshot rather than historical affiliation on each paper. These are publication measures, not undergraduate teaching-quality measures. Consult the [pinned implementation](https://github.com/emeryberger/CSrankings/blob/5e8a27d68310c728a182b8bb3b6437c39bce0cad/csrankings.js) for precise rules before any authorized implementation.

## Missingness and permissions

Eligibility concerns institutions with CS doctoral programs and full-time research faculty eligible to advise CS PhDs; many liberal arts colleges are outside scope. Future observations must distinguish outside scope, listed but no selected publications, unresolved alias, unavailable, and observed. Currently every numeric observation is null with `permission_required`, not zero or last place.

The official FAQ identifies its code/data license as CC BY-NC-ND 4.0 and restricts redistribution of material built from it. See [COPYING](https://github.com/emeryberger/CSrankings/blob/5e8a27d68310c728a182b8bb3b6437c39bce0cad/COPYING). Link-outs and original methodology descriptions are published here; derived ranking data is not.
