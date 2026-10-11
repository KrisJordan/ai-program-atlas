# Artificial Intelligence/Machine Learning — curriculum review

Reviewed 2026-10-10. Status: **partial**.

A formally declared AI/Machine Learning concentration within the CS BS. Local course requirements remain behind an inaccessible catalog.

The adapter parses the current department HTML and refuses missing identities, material policy changes, access pages and unrelated concentration rows. It never emits a completeness audit or verification date.

Reviewed sections:

- Concentration selection at CS major declaration

Outstanding requirements:

- AI/ML-specific required and elective courses, choice rules and concentration completion policies remain inaccessible.

Curriculum evidence reviewed on 2026-10-10. The official catalog returned a JavaScript/robot challenge; no access restriction was bypassed. Department sources support the observations below, but a full catalog audit remains outstanding. Course metadata remains unverified; unknown credits and calendar are not inferred.

Sources:

- https://cdsp.wm.edu/computerscience/undergraduate/bachelor-of-science-b.s-in-computer-science.php?mapstat=1

## Public policy follow-up — 2026-10-11

Registrar PDF reviewed: https://www.wm.edu/offices/registrar/_documents/degree/declaration_of_major_form.pdf (Page 1; printed revision August 2025). Corroborating department links: https://cdsp.wm.edu/computerscience/resources/ . Current central directory: https://www.wm.edu/offices/advising/academic-forms/ . The documents are general W&M forms; the major form explicitly includes CDSP, and the minor form states general undergraduate constraints. Only applicable credential/host-major policies were added; no requirements from other named professional schools or the self-designed major procedure were assigned.

Added 3 requirement notes. Inventory stays **partial**. General minor residence is conditional on catalog exceptions; exact program course lists, applicable overlap rules and existing source conflicts are unchanged. The central directory now calls the exception body the Committee on Academic Exceptions, replacing the Committee on Degrees still printed in the minor form. No exception is assumed. Credit amounts retain their original wording and unknown normalized unit.

The HTML source parser hashes only the relevant form categories and Registrar listings, producing observations for review. The PDF is public and was read as a document; the standard Fetcher correctly reports a non-text-format limitation after permitted retrieval. PDF facts therefore require a separate format review: extract text from the exact official document, inspect its rendering, then run `parse_reviewed_declaration_text(text, PROGRAM_ID, minor=False)` from `william_mary_public_policies`. This returns a change-detectable observation, never an audit or automatic policy replacement. No PDF or whole-page copy is committed. Known catalog gates were not retried.
