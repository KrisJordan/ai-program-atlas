# RIT Mathematics immersion branch — 2026-10-11

Reviewed the ordinary public [Mathematics Immersion page](https://www.rit.edu/study/mathematics-immersion)
in Chrome: overview, 2026–2027 curriculum, two tables, footnotes and all 37 exact
course popups. An initial popup still said “Loading course description”; that
was not counted as evidence and was reread after its exact identity appeared.
The HTTP source lacks the rendered tables, so its identity shell is not treated
as an automated curriculum observation. No restricted catalog endpoint was
requested outside normal page behavior.

The menu lists 30 electives, choose three with at least one at the 300 level.
The selection-row range is 9–12 semester hours and the total row says 9; preserve
both, since variable course amounts need not contradict a minimum total. Seven
prerequisite identities are separate: MATH181 or the MATH171+172 sequence, then
a second menu listing MATH182, MATH173, MATH190 and MATH200. Neither preparation
nor all alternatives are extra fixed degree requirements.

The route explicitly prohibits overlap with program requirements. AI-fixed
MATH241 and MATH251 remain in the source manifest but are excluded from the
AI-specific immersion choice node. This leaves 28 conditional options and adds
three preparation-only identities. The aggregate becomes **23 fixed / 45 options
/ 6 unresolved-context = 74**. Six existing degree identities retain their prior
source-specific metadata/review; current matching cards were corroborative, not
a new alias relation. The 31 added records have 28 mathematics, one historical
human-context, one cryptography/systems and one mixed subject disposition. The
other 76 public immersion branches remain accessible work, so the primary audit
is still in progress.

Course interpretation is based on actual descriptions. MATH291 centers on
historical discoveries and mathematicians. MATH367 centers on encryption,
public-key techniques and hashes, supported by mathematics. MATH367H separately
emphasizes those methods, algebraic tools and historical primary documents; it
remains mixed systems/mathematics/human context. Graph theory, optimization and
simulation center on mathematical concepts/methods despite computational uses;
mentions of AI applications in classical game theory do not make it an AI course.

Exact restrictions remain visible: 219/221 and 231/233 cannot both satisfy their
footnoted selection; 221H separately excludes credit with 219/221. No exclusion
is treated as cross-list identity. Honors221H/241H use 3.2 GPA alternatives,
367H uses 3.3, and their published Boolean prerequisites are not editorially
rewritten. MATH233 names only CHEM-BS, CHEM-BS/MS and ISEE-BS audiences; the already
reviewed D03.0 permission process is a conditional path, not a granted AI waiver.
Legacy prerequisite numbers and MATH190 co-requisites are retained.

`rit_mathematics_immersion_reviews.json` contains manually reviewed concise
summaries and exact entry conditions. `rit_mathematics_immersion.parse` reads
actual rendered tables/cards, separating prerequisite and elective observations;
it accepts honors suffixes, preserves source amounts, rejects identity/version
shells and never emits manual reviews or completion. The semester normalization
comes from separately reviewed D01.4 rather than the word “Credits” in a popup.
Synthetic fixtures exercise changed amounts, roles, entry conditions and failed
contexts; they are clearly separate from source text. Existing RIT-specific
legacy count assertions are updated without changing Buffalo/Delaware cases.
