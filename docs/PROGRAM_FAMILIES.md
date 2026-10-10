# Program families and concrete variants

A family groups independently addressable programs after evidence review. It is not an award, an institution, or a replacement for a degree record. A family's classification can be university-stated or explicitly analyst-classified; resemblance between titles is insufficient evidence. Existing program IDs, detail URLs, and comparison URLs remain unchanged.

The initial research case is Northeastern's combined AI degrees with Biology, Philosophy and Business Administration. The institution describes combined majors as designed two-discipline degrees with integration. Review of each catalog identifies a small identical AI/computing core. Different mathematics, seminars, advanced choices, partner requirements and integration courses must not be collapsed into that core.

## Stored structure

`data/families/<id>.json` and relational family tables store shared requirement facts once. The family has sources and a reviewed collection of shared requirement nodes, using `course_codes` to identify their scope. Each concrete program retains its independently sourced course observations, title, award, hosting unit, policies and additional requirements. These course observations can legitimately differ by catalog and source; they are not treated as one globally interchangeable course.

A program's optional `family` object contains a family ID, concrete variant label, disciplinary partners, relationship (`ai_plus_x`, `x_plus_ai`, `integrated`, or `unknown`), classification basis, sources, and hosting units. A relationship is not inferred from title order and does not imply curricular dominance.

`requirement_bindings` associate each shared definition with its original program requirement ID, parent ID, local course IDs and local catalog source. They contain identifiers and provenance, not copied requirement facts. This preserves existing references and documents that the shared rule was checked in each variant's catalog. The corresponding duplicate nodes are removed from the live program requirement list. Historical revision snapshots remain intact.

Variant requirements are additions. `requirement_overrides` explicitly record exclusions or replacements of shared nodes, with a reason and a program source. A replacement must have the bound original ID; silent collisions are rejected. Missing bindings, dangling parents, cycles, incompatible course-code bindings, and unknown evidence references fail validation. Optional component annotations identify an AI core, domain component, integration component or other scope only where reviewed, with their classification basis and sources.

## Resolution and publication

The exporter resolves the shared definitions, explicit changes and local additions into the existing complete program requirement view. Each node carries its origin (`family`, `variant`, or `replacement`) and, when applicable, a shared requirement ID and reviewed component. Comparison remains between concrete program IDs. Families can be expanded in the listing and filtered by disciplinary partner; family, variant, award and institution counts stay separate.

Program adapters continue observing each official source independently and never certify a shared family merely because extracted nodes match. Candidate review compares observations against the resolved program. A family revision is validated against its dependent variants; unresolved source differences must be reviewed before publication. No family inheritance promotes curriculum completeness automatically.

## Review and transaction safeguards

Family definitions retain their exact reviewed JSON shape as well as normalized relational rows, so optional source fields and annotations survive round trips without changing the review hash. Each complete inherited program must record `curriculum_audit.family_content_hash` equal to the reviewed family's content hash. Changing the shared definition therefore requires an explicit refreshed audit for complete dependents; partial programs remain partial.

The ingest command applies the cohort, family definitions, affected variants and surveys in one transaction. A malformed source, stale audit, broken binding or failed foreign key rolls back the entire batch. Direct family updates also validate every existing dependent and apply supplied program revisions atomically. Identical reruns add no revisions, preserve manual overrides and keep resolved requirement IDs stable.
