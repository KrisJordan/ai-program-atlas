# CSRankings research context — import held

Verified 2026-10-10 against the [official FAQ](https://csrankings.org/faq) and pinned [September 28, 2026 source snapshot](https://github.com/emeryberger/CSrankings/commit/5e8a27d68310c728a182b8bb3b6437c39bce0cad). No source dataset or implementation is included in this repository. Public numeric import is held pending permission or qualified reuse review; this is a project limitation, not a claim that every factual citation is prohibited.

## Proposed reproducible configuration

Five fields, separately and in an aggregate: `ai`, `vision`, `mlmining`, `nlp`, `inforet`. Default venues are AAAI/IJCAI; CVPR/ECCV/ICCV; ICLR/ICML/NeurIPS; ACL/EMNLP/NAACL; and SIGIR/WWW. KDD is a separate next-tier toggle, disabled by default; robotics is outside this AI group. Proposed project window: **2016–2025**, ten completed calendar years; geographic filter **us**. This is a project choice, not the site's current default. The current default spans current year minus ten through current year inclusive, and thus includes incomplete 2026.

A future authorized calculation should rank all eligible U.S. institutions first, then join the atlas cohort with reviewed institution aliases. Record snapshot, year bounds, country, venue toggles, crosswalk and rounding. Preserve individual field observations and explicit field membership for the aggregate. Do not average ordinal ranks.

The FAQ describes equal fractional credit across all authors and a geometric aggregation of adjusted field counts plus one. The pinned implementation rounds displayed aggregate values to one decimal before competition ranking. It does not normalize by faculty size. Affiliation reflects the selected snapshot rather than historical affiliation on each paper. These are publication measures, not undergraduate teaching-quality measures. Consult the [pinned implementation](https://github.com/emeryberger/CSrankings/blob/5e8a27d68310c728a182b8bb3b6437c39bce0cad/csrankings.js) for precise rules before any authorized implementation.

## Missingness and permissions

Eligibility concerns institutions with CS doctoral programs and full-time research faculty eligible to advise CS PhDs; many liberal arts colleges are outside scope. Future observations must distinguish outside scope, listed but no selected publications, unresolved alias, unavailable, and observed. Currently every numeric observation is null with `permission_required`, not zero or last place.

The official FAQ identifies its code/data license as CC BY-NC-ND 4.0 and restricts redistribution of material built from it. See [COPYING](https://github.com/emeryberger/CSrankings/blob/5e8a27d68310c728a182b8bb3b6437c39bce0cad/COPYING). Link-outs and original methodology descriptions are published here; derived ranking data is not.
