# Curriculum review and completeness

`curriculum_status` describes the requirement inventory for the represented program. It does not describe institutional search coverage, course metadata completeness, teaching quality, or an individual student's eligibility to graduate.

- `pending`: no reviewed requirement inventory yet.
- `partial`: some requirements mapped, with unresolved inventory or rule gaps.
- `complete`: a reviewer has represented all published applicable requirements, choice rules, prerequisite or admission conditions, overlap and grade policies, and completion constraints in the cited scope. An open-ended advisor-approved option can be complete when the approval rule is explicitly represented; an unavailable finite approved list remains a gap.

For degrees, scope includes the published major and degree-wide requirements, including linked college/general education requirements. For minors, concentrations, and additional majors, scope is that credential's own requirements and eligibility/relationship to the host degree. A complete concentration does not claim that the host degree's whole curriculum is mapped. Requirement `note` nodes can express policies that cannot safely be reduced to a course count. The tree is an evidence-backed representation, not an automated graduation audit.

Course descriptions, prerequisites, credits, public course sites, and example syllabi are separate metadata dimensions. A missing prerequisite value means unverified, never that the course has no prerequisites. Missing metadata does not by itself make a fully reviewed requirement inventory partial, but it must remain visible. Prerequisites that the program explicitly requires for admission or completion belong in the requirement inventory as well.

Complete records require a `curriculum_audit` object:

```json
{
  "scope": "minor",
  "reviewed_at": "2026-10-10",
  "source_ids": ["official-catalog"],
  "sections": ["Required courses", "Elective alternatives", "Grade and overlap policies"],
  "unresolved_requirements": [],
  "metadata_gaps": ["Public syllabi not yet verified"]
}
```

`scope` equals `program_kind`; `source_ids` reference this record's sources. `sections` names the portions actually reviewed, with precise locators in those source records and adapter notes. Partial records may carry the same audit with explicit unresolved requirements. `reviewed_at` is the date of the human/agent evidence review, not a timestamp emitted by a scraper. Scrapers collect observations and candidates; they never promote completeness or manufacture this audit. A changed source should trigger review, not erase curated facts or automatically recertify them.

Completeness is a documented research judgment. Structural validation checks the evidence references and audit consistency; it cannot prove that a source has been exhaustively interpreted. Adapter notes must record edge cases and the basis for that judgment, and focused tests should exercise alternatives and changed requirements.
