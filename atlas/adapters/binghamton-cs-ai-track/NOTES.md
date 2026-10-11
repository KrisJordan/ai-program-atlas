# Binghamton — BSCS with Artificial Intelligence Track

Reviewed 2026-10-11. This is a formal optional track within BS Computer Science, not a separate bachelor's award. Identity and four-course structure are current official department evidence. First offering remains unknown; September 10, 2026 is a page update.

## Evidence and extraction

- [Department track page](https://www.binghamton.edu/computer-science/undergraduate-programs/bs-aitrack.html): two required courses, two electives, eleven eligible department-listed options. Ordinary permitted HTTP and Chrome inspection both succeeded. Dynamic course widgets displayed loading text, but public HTML declares their exact CS course codes. The parser reads these ordinary markup attributes and inline course text, bounded by the Required courses/Electives headings; no widget API is called.
- [Official linked flyer](https://drive.google.com/file/d/1RGfWJB0KD29KudczS1EHFLGz7ZVDudHo/view): one-page public Drive preview, read and visually inspected without authentication; names and course roles corroborate department entries. Original names are factual metadata, not a reproduced flyer. It permits 4+1 and completing the track at BS/MS level, and also pursuing Cybersecurity. This does not establish course overlap between tracks.
- [Current Fall 2026 BSCS guide](https://www.binghamton.edu/watson/student-services/advising/undergrad-forms/cs26.pdf), linked from the current undergraduate directory: two pages visually reviewed, with page 2's two-column table and footnotes checked. Printed June 2026, exact day unknown. Eleven course prerequisites normalized from that table. Slash alternatives are explicitly defined; prerequisite C- rule retained. CS 417 and CS 481E missing from the prerequisite table remain null. Flyer names sometimes omit the guide's Intro/Introduction prefix; exact course codes anchor identities.
- Semester units follow the guide's explicit semester-credit wording. Only CS 481E's three credits are known from the track page. No total is computed from unknown amounts. The degree's 126-credit and GPA minima are host context, not local track credits or a completed full BS curriculum.

## Conflict and limits

The guide's track paragraph omits CS 417, although the current department page and linked flyer include it. The guide refers to certain CS 480 courses; the department currently lists CS 481E. Preserve the department pool and make the discrepancy visible, pending reconciliation. Track electives must still respect BSCS breadth areas A/B/C; track completion alone does not satisfy every host-degree rule.

Direct catalog HTTP 403 and unresolved widgets are recorded as access limits; no restriction was bypassed. The older printable cs25 page linked from another department page was not substituted for the current cs26 guide. Track declaration, local grade treatment, transfer/residence applicability and source reconciliation remain next checks. Host BS learning outcomes were not copied as track outcomes. Course descriptions, public sites and syllabi remain unverified.

## Reruns

`parse(html)` extracts the actual current course identities into observed candidates, preserves the two-plus-two rule, detects missing groups/empty lists and refuses a changed required count. It never emits verification dates or a completeness audit. New or changed elective identities become a reviewable candidate; the reviewed seed's PDF/flyer metadata is not fabricated by the HTML parser. Synthetic fixtures cover widget/inline mixing, neighboring content exclusion, changed options, missing content and rule changes. Raw HTML/PDF and images stay in ignored cache or `/tmp`, outside public commits.
