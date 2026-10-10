"""Dependency-free, escaped static publishing for the AI Program Atlas."""
from __future__ import annotations

from collections import Counter
from html import escape
import json
from pathlib import Path
import re
import shutil

CATEGORIES = {
    "foundations": "Computing foundations", "mathematics": "Mathematics",
    "ai_ml": "AI & machine learning", "systems": "Systems",
    "human_context": "Human context", "applications": "Applications",
    "electives": "Electives", "other": "Other / unclassified",
}


def esc(value):
    return escape(str(value if value is not None else "Unknown"), quote=True)


def human(value):
    return str(value or "unknown").replace("_", " ").capitalize()


def safe_url(value):
    value = str(value or "")
    return value if value.startswith(("https://", "http://")) else ""


def external(url, label):
    url = safe_url(url)
    return f'<a href="{esc(url)}" rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>' if url else esc(label)


def unique_courses(program):
    return list({c["id"]: c for c in program.get("courses", []) if c.get("id")}.values())


def shell(title, body, base, current="", payload=None):
    current_attr = 'aria-current="page"'
    nav = "".join(f'<a {current_attr if current == key else ""} href="{base}{path}">{label}</a>' for key, path, label in [
        ("atlas", "", "Explore programs"), ("coverage", "coverage/", "Coverage"), ("methodology", "methodology/", "Methodology")])
    script = ""
    if payload is not None:
        serialized = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        script = f'<script id="atlas-data" type="application/json">{serialized}</script><script src="{base}assets/atlas.js" defer></script>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · AI Program Atlas</title><meta name="description" content="A source-backed field guide to undergraduate artificial intelligence programs, curricula, and research context.">
<link rel="stylesheet" href="{base}assets/atlas.css"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="brand" href="{base}" aria-label="AI Program Atlas home"><span class="brand-mark" aria-hidden="true">A<span>i</span></span><span>AI Program Atlas<small>UNDERGRADUATE FIELD GUIDE</small></span></a><nav aria-label="Main navigation">{nav}</nav></header>
<main id="main">{body}</main>
<footer><span>AI Program Atlas <span class="muted">/ An open research index</span></span><a href="{base}methodology/">Evidence before inference <span aria-hidden="true">↗</span></a><p>Programs change. Confirm requirements with the institution’s current official catalog.</p></footer>{script}</body></html>'''


def badge(text, kind=""):
    return f'<span class="badge {esc(kind)}">{esc(text)}</span>'


def date_value(p):
    return p.get("last_verified") or "Not recorded"


def evidence_label(p):
    labels = {'pending': 'Pending — identity only', 'complete': 'Complete requirement inventory', 'partial': 'Partial requirement inventory'}
    return labels.get(p.get('curriculum_status'), 'Unknown')


def curriculum_scope(p):
    kind = p.get('program_kind')
    scope = {
        'concentration': 'This inventory covers the concentration’s local requirements, not the whole parent degree.',
        'minor': 'This inventory covers the minor’s requirements, not the student’s whole degree.',
        'additional_major': 'This inventory covers the additional major’s requirements, not the primary degree or every graduation requirement.',
        'degree': 'This inventory covers the represented degree program at the recorded catalog year.',
    }.get(kind, 'This inventory covers only the represented award or program.')
    state = {
        'complete': 'Complete means the requirement inventory for this represented award has been extracted from the recorded sources.',
        'partial': 'Partial means some of this program’s requirement inventory remains unextracted.',
        'pending': 'Pending means program identity is documented; its requirement inventory has not yet been extracted.',
    }.get(p.get('curriculum_status'), 'Requirement inventory completeness has not been established.')
    return state + ' ' + scope + ' Course metadata completeness is assessed separately below. Listed electives and alternatives are options; every listed course is not necessarily required.'


def metadata_availability(p):
    courses = unique_courses(p)
    sources = {s.get('id'): s for s in p.get('sources', [])}
    def sourced(course):
        return bool(safe_url(course.get('url')) or safe_url(sources.get(course.get('source_id'), {}).get('url')))
    fields = [('description', 'Descriptions'), ('prerequisites', 'Prerequisite statements'), ('credits', 'Credit amounts'), ('credit_unit', 'Known credit units')]
    counts = [(label, sum(sourced(c) and c.get(key) is not None and c.get(key) != '' and (key != 'credit_unit' or c.get(key) != 'unknown') for c in courses)) for key, label in fields]
    return '<section class="metadata-availability" aria-labelledby="metadata-title"><h3 id="metadata-title">Course metadata availability</h3><p class="section-note">Counts below show populated fields with a recorded course or source URL, across ' + str(len(courses)) + ' unique course records. They describe evidence availability, not requirement completeness. A missing prerequisite statement does not mean “no prerequisites”; an unknown credit unit cannot be converted or totaled.</p><dl class="metadata-counts">' + ''.join(f'<div><dt>{esc(label)}</dt><dd><strong>{count}</strong> of {len(courses)} sourced</dd></div>' for label, count in counts) + '</dl></section>'


def program_card(p, base):
    institution = p.get("institution", {})
    courses = unique_courses(p)
    return f'''<article class="program-card" data-program-id="{esc(p['id'])}">
<div class="card-top"><span class="eyebrow">{esc(institution.get('name'))}</span><span class="card-badges">{badge(human(p.get('program_kind')))}{badge(p.get('award_level')) if p.get('award_level') not in ('other', 'minor', 'concentration', None) else ''}</span></div>
<h3><a href="{base}programs/{esc(p['id'])}/">{esc(p.get('title'))}<span aria-hidden="true">↗</span></a></h3>
<p class="card-description">{esc(p.get('overview') or 'Program overview has not yet been recorded.')}</p>
<dl class="card-facts"><div><dt>Academic calendar</dt><dd>{esc(human(institution.get('calendar')))}</dd></div><div><dt>Curriculum evidence</dt><dd>{esc(evidence_label(p))}</dd></div></dl>
<div class="card-evidence"><span>{len(courses)} course records</span><span>Verified {esc(date_value(p))}</span></div>
<div class="card-bottom"><a href="{base}programs/{esc(p['id'])}/">View program <span aria-hidden="true">→</span></a><label class="compare-choice js-only"><input type="checkbox" data-compare="{esc(p['id'])}"> Compare<span class="sr-only"> {esc(p.get('title'))} at {esc(institution.get('name'))}</span></label></div></article>'''


def limitations(meta):
    values = meta.get("limitations") or []
    if isinstance(values, str):
        values = [values]
    return "".join(f"<li>{esc(v)}</li>" for v in values)


def options(values):
    return "".join(f'<option value="{esc(key)}">{esc(label)}</option>' for key, label in values)


def root_page(data, base):
    programs = data.get("programs", [])
    institutions = data.get("institutions", [])
    meta = data.get("meta", {})
    cohort = meta.get("cohort")
    cohort_label = cohort if isinstance(cohort, str) else f"U.S. News {cohort.get('edition', 'edition unverified')} target cohorts · incomplete inventory" if isinstance(cohort, dict) else "U.S. undergraduate programs · source-backed pilot"
    summary = meta.get("coverage_summary")
    identity_only = sum(p.get('curriculum_status') == 'pending' for p in programs)
    summary = summary if isinstance(summary, str) else f"{len(programs)} documented programs; {identity_only} identity-only records await curriculum extraction. Institution and cohort coverage remain incomplete. An unlisted program is not evidence of absence."
    filters = [
        ("type", "Program type", [("degree", "Degree"), ("additional_major", "Additional major"), ("minor", "Minor"), ("concentration", "Concentration")]),
        ("award", "Award", sorted({(p.get("award_level", "other"), p.get("award_level", "Other")) for p in programs})),
        ("evidence", "Curriculum evidence", [("pending", "Pending — identity only"), ("partial", "Partial requirements"), ("complete", "Complete requirements")]),
        ("calendar", "Calendar", sorted({(p.get("institution", {}).get("calendar") or "unknown", human(p.get("institution", {}).get("calendar"))) for p in programs})),
        ("institution", "Institution", sorted({(p.get("institution", {}).get("id", ""), p.get("institution", {}).get("name", "Unknown")) for p in programs}, key=lambda v: v[1])),
        ("cohort", "Institution category", [("National Universities", "National Universities"), ("National Liberal Arts Colleges", "National Liberal Arts Colleges")]),
        ("category", "Course category", list(CATEGORIES.items())),
    ]
    controls = "".join(f'<label for="filter-{key}">{label}<select id="filter-{key}" name="{key}"><option value="">All</option>{options(vals)}</select></label>' for key, label, vals in filters)
    body = f'''<section class="hero"><div><div class="eyebrow"><span class="status-dot"></span> THE UNDERGRADUATE AI LANDSCAPE</div><h1>Find the program.<br><em>Understand the curriculum.</em></h1><p class="lede">A source-backed field guide to undergraduate artificial intelligence. Explore what programs teach, compare their structure, and follow the evidence.</p></div><aside class="edition-note"><span class="eyebrow">RESEARCH EDITION</span><strong>{len(programs):02d}</strong><span>documented programs</span><p>{esc(cohort_label)}</p><a href="{base}coverage/">Read the coverage notes →</a></aside></section>
<div class="coverage-strip"><span class="eyebrow">A WORK IN PROGRESS</span><p>{esc(summary)}</p><a href="{base}coverage/">Coverage & limitations <span aria-hidden="true">↗</span></a></div>
<section class="explorer" aria-labelledby="explore-title"><div class="section-heading"><div><span class="eyebrow">01 / PROGRAM INDEX</span><h2 id="explore-title">Explore the atlas</h2></div><p>Follow the curriculum, not a score.</p></div>
<form id="filters" class="filters js-only" role="search"><label class="search-label" for="search">Search programs<input type="search" id="search" name="q" placeholder="Institution, program, or course…" autocomplete="off"></label><div class="filter-row">{controls}<button type="button" id="reset-filters" class="text-button">Reset filters</button></div><p class="filter-help">Course category filters use documented course records; partial curricula may omit matching courses.</p></form>
<noscript><p class="notice">All documented programs are listed below. Enable JavaScript to filter and compare programs.</p></noscript>
<div class="results-heading"><p id="result-count" role="status" aria-live="polite">{len(programs)} programs</p><span>Alphabetical by institution</span></div>
<div class="program-grid" id="program-grid">{''.join(program_card(p, base) for p in sorted(programs, key=lambda p: p.get('institution', {}).get('name', '')))}</div>
<div id="empty-state" class="empty-state" hidden><span class="eyebrow">NO MATCHES</span><h3>A narrower search needs a wider lens.</h3><p>No documented program matches these filters. This does not establish that such a program does not exist.</p><button type="button" id="empty-reset">Clear filters</button></div></section>
<div id="compare-tray" class="compare-tray" hidden><span id="tray-count">0 of 4 selected</span><a href="#comparison">Compare programs ↓</a></div><section id="comparison" class="comparison js-only" aria-labelledby="compare-title"><div class="section-heading"><div><span class="eyebrow">02 / SIDE BY SIDE</span><h2 id="compare-title">Compare with context</h2></div><button type="button" id="clear-comparison" class="text-button">Clear selection</button></div><p class="comparison-intro">Choose up to four programs. Credit units and incomplete curricula stay visible; course counts are not measures of program quality.</p><div id="compare-status" role="status" aria-live="polite"></div><div id="comparison-content"><p class="comparison-placeholder">Select “Compare” on a program to begin.</p></div></section>
<section class="method-callout"><span class="eyebrow">BUILT TO BE INSPECTED</span><h2>Every program has a paper trail.</h2><p>Official sources, verification dates, requirement structure, and unknowns travel with the data. Source-stated outcomes are kept separate from editorial classifications.</p><a href="{base}methodology/">How to read this atlas →</a></section>'''
    return shell("Explore undergraduate AI programs", body, base, "atlas", {"programs": programs, "institutions": institutions, "base_path": base, "categories": CATEGORIES})


def category_chart(p):
    courses = unique_courses(p)
    if not courses:
        return '<div class="notice"><strong>Curriculum profile not yet extracted.</strong><p>No course records are available for this program. Category coverage is unknown; missing records do not mean the curriculum contains zero courses in a category.</p></div>'
    counts = Counter(c.get("category") if c.get("category") in CATEGORIES else "other" for c in courses)
    maximum = max(counts.values(), default=1)
    return f'<p class="section-note">{len(courses)} unique documented course records. Each course appears in one editorial category. These are observed counts, not credit totals or proportions of a degree; electives and partial extraction affect the picture.</p><div class="category-chart">' + "".join(f'<div class="category-row"><span>{label}</span><div class="bar-track"><span class="bar" style="width:{counts[key] / maximum * 100:.2f}%"></span></div><strong>{counts[key]}</strong></div>' for key, label in CATEGORIES.items()) + '</div>'


def requirement_tree(p):
    requirements = p.get("requirements", [])
    course_map = {c["id"]: c for c in unique_courses(p)}
    ids = {r.get("id") for r in requirements}
    sources = {s.get('id'): s for s in p.get('sources', [])}
    rendered = set()

    def render(r, seen):
        rid = r.get("id")
        if rid in seen:
            return ""
        seen = seen | {rid}
        rendered.add(rid)
        requirement_courses = [course_map[cid] for cid in dict.fromkeys(r.get("course_ids") or []) if cid in course_map]
        courses = "".join(f'<li><a href="#course-{esc(c["id"])}">{esc(c.get("code") or "Code unknown")} · {esc(c.get("name") or "Course name not verified")}</a></li>' for c in requirement_courses)
        children = "".join(render(child, seen) for child in requirements if child.get("parent_id") == rid)
        selection = []
        if r.get("count") is not None:
            selection.append(f'{r["count"]} course' + ('' if r['count'] == 1 else 's'))
        if r.get("credits") is not None:
            selection.append(f'{r["credits"]} {human(r.get("credit_unit"))}')
        course_list = '<p class="course-list-label">Listed courses / options — follow the group rule</p><ul class="requirement-courses">' + courses + '</ul>' if courses else ''
        operator = {'all': 'Complete all items in this group', 'choose_courses': 'Choose courses', 'choose_credits': 'Choose by credit amount', 'alternative': 'Choose an alternative', 'note': 'Requirement note'}.get(r.get('kind'), human(r.get('kind')))
        source = sources.get(r.get('source_id'), {})
        evidence = '<p class="requirement-evidence">' + external(source.get('url'), 'Requirement source') + '</p>' if source else '<p class="requirement-evidence">Requirement source not recorded.</p>'
        source_wording = '<details class="source-wording"><summary>Source wording</summary><blockquote>' + esc(r['source_text']) + '</blockquote></details>' if r.get('source_text') else ''
        return f'<li class="requirement"><div>{badge(operator)}<h3>{esc(r.get("title"))}</h3></div>{"<p>" + esc(" · ".join(selection)) + "</p>" if selection else ""}<p>{esc(r.get("summary") or "Requirement detail has not been extracted.")}</p>{source_wording}{course_list}{"<ul>" + children + "</ul>" if children else ""}{evidence}</li>'

    roots = [r for r in requirements if not r.get("parent_id") or r.get("parent_id") not in ids]
    if not requirements:
        return '<p class="notice">Requirement structure has not yet been extracted. Consult the official catalog.</p>'
    content = ''.join(render(r, set()) for r in roots)
    remaining = [r for r in requirements if r.get('id') not in rendered]
    if remaining:
        content += '<li class="notice">Some recorded groups have unresolved parent relationships. Their recorded rules are shown below; consult the source for their placement.</li>'
        for r in remaining:
            if r.get('id') not in rendered:
                content += render(r, set())
    return '<ul class="requirements">' + content + '</ul>'


def outcomes(p, kind):
    values = [o for o in p.get("outcomes", []) if o.get("kind") == kind]
    sources = {s.get("id"): s for s in p.get("sources", [])}
    if not values:
        return '<p class="muted">Not yet recorded.</p>'
    return '<ul class="outcomes">' + ''.join(f'<li>{esc(o.get("text"))}<small>{external(sources.get(o.get("source_id"), {}).get("url"), "Source")} · {esc(o.get("locator") or "Locator not recorded")}</small></li>' for o in values) + '</ul>'


def program_page(p, base):
    institution = p.get("institution", {})
    courses = unique_courses(p)
    first = p.get("first_offered")
    first_text = "Unknown — not established by the available evidence"
    if first:
        first_text = external(first.get("evidence_url"), first.get("value")) + ' <small>' + esc(first.get("uncertainty") or first.get("precision") or "") + '</small>'
    links = ' <span aria-hidden="true">/</span> '.join(external(link.get("url"), link.get("label") or human(link.get("kind"))) for link in p.get("links", []))
    missing_credits = sum(c.get("credits") is None for c in courses)
    rows = ''.join(f'''<tr><th scope="row" id="course-{esc(c['id'])}">{esc(c.get('code') or 'Unknown')}<span>{esc(c.get('name') or 'Course name not verified')}</span><p class="course-description">{esc(c.get('description') or 'Description not recorded.')}</p></th><td>{esc(CATEGORIES.get(c.get('category'), CATEGORIES['other']))}</td><td>{esc(c.get('credits'))}<small>{esc(human(c.get('credit_unit')))}</small></td><td>{esc(c.get('prerequisites') or 'Not recorded')}</td><td>{external(c.get('url'), 'Catalog')}{'<br>' + external(c.get('public_site'), 'Course site') if c.get('public_site') else ''}{'<br>' + external(c.get('syllabus'), 'Syllabus') if c.get('syllabus') else ''}</td></tr>''' for c in courses)
    sources = ''.join(f'''<li id="source-{esc(s.get('id'))}"><h3>{external(s.get('url'), s.get('title') or 'Official source')}</h3><p>{esc(s.get('locator') or 'Locator not recorded')}</p><dl class="source-meta"><div><dt>Retrieved</dt><dd>{esc(s.get('fetched_at') or 'Not recorded')}</dd></div><div><dt>Source date</dt><dd>{esc(s.get('source_date'))}</dd></div><div><dt>Catalog year</dt><dd>{esc(s.get('catalog_year'))}</dd></div><div><dt>Confidence</dt><dd>{esc(human(s.get('confidence')))}</dd></div></dl></li>''' for s in p.get('sources', []))
    notes = ''.join(f'<li>{esc(n)}</li>' for n in p.get('notes', []))
    rankings = institution.get('rankings') or []
    ranking_context = '<section class="cohort-context" aria-label="Institution ranking context"><h2>Cohort context</h2><p>Institution-level U.S. News category membership, not a measure of this program or undergraduate teaching quality. Ranks from different categories are not comparable.</p>'
    if rankings:
        ranking_context += '<ul>'
        for rank in rankings:
            label = f"{rank.get('publisher', 'U.S. News')} {rank.get('edition', 'edition unknown')} · {rank.get('category', 'Category unknown')} · #{rank.get('rank', 'unknown')}"
            ranking_context += f'<li>{external(rank.get("source_url"), label)}<small>Membership evidence: {esc(human(rank.get("verification_status")))}</small></li>'
        ranking_context += '</ul>'
    else:
        ranking_context += '<p>Ranking provenance is not recorded for this institution.</p>'
    ranking_context += '</section>'
    body = f'''<div class="breadcrumb"><a href="{base}">Program index</a><span>/</span>{esc(institution.get('name'))}</div><section class="detail-hero"><div class="eyebrow">{esc(institution.get('name'))} / {esc(p.get('hosting_unit') or 'Hosting unit unknown')}</div><h1>{esc(p.get('title'))}</h1><p class="lede">{esc(p.get('overview') or 'Overview not yet recorded.')}</p><div class="detail-badges">{badge(p.get('award_level'))}{badge(human(p.get('program_kind')))}{badge(human(p.get('status')))}</div><div class="official-links">{links}</div></section>
<dl class="fact-grid"><div><dt>Calendar</dt><dd>{esc(human(institution.get('calendar')))}</dd></div><div><dt>Catalog year</dt><dd>{esc(p.get('catalog_year'))}</dd></div><div><dt>Last verified</dt><dd>{esc(date_value(p))}</dd></div><div><dt>Requirement inventory</dt><dd>{esc(evidence_label(p))}</dd></div></dl>
<div class="notice evidence-notice"><strong>Read the evidence in context.</strong><p>Verification: {esc(human(p.get('verification_status')))}. {missing_credits} of {len(courses)} course records have unknown credits. Unknown values are not zero. Recorded course credits must not be added to estimate degree requirements.</p><p class="curriculum-scope">{esc(curriculum_scope(p))}</p><p>First offered: {first_text}</p>{'<ul>' + notes + '</ul>' if notes else ''}</div>{ranking_context}
<nav class="section-nav" aria-label="Program sections"><a href="#curriculum">Curriculum</a><a href="#requirements">Requirements</a><a href="#outcomes">Outcomes</a><a href="#courses">Course records</a><a href="#sources">Sources</a></nav>
<section id="curriculum" class="detail-section"><span class="eyebrow">01 / CURRICULUM PROFILE</span><h2>What the documented courses cover</h2>{category_chart(p)}</section>
<section id="requirements" class="detail-section"><span class="eyebrow">02 / PROGRAM STRUCTURE</span><h2>Requirements & choices</h2><p class="section-note">Nested groups preserve course choices and alternatives. A course listed in more than one group is counted once in the curriculum profile. Follow each group’s rule: elective pools and alternative paths do not make every listed course compulsory.</p>{requirement_tree(p)}</section>
<section id="outcomes" class="detail-section"><span class="eyebrow">03 / LEARNING OUTCOMES</span><h2>Intent, with attribution</h2><div class="outcome-grid"><div><h3>Source-stated outcomes</h3><p class="section-note">Statements attributed to the institution, summarized from official evidence.</p>{outcomes(p, 'source_stated')}</div><div><h3>Inferred taxonomy</h3><p class="section-note">Editorial classifications. These are interpretations, not claims made by the institution.</p>{outcomes(p, 'inferred_taxonomy')}</div></div></section>
<section id="courses" class="detail-section"><span class="eyebrow">04 / COURSE RECORDS</span><h2>Inspect the building blocks</h2>{metadata_availability(p)}<p class="section-note">Credits retain their original units. “Not recorded” means the atlas lacks evidence; it does not mean a course has no prerequisites.</p><div class="table-scroll" role="region" aria-label="Course records" tabindex="0"><table class="course-table"><thead><tr><th scope="col">Course</th><th scope="col">Category</th><th scope="col">Credits</th><th scope="col">Prerequisites</th><th scope="col">Evidence</th></tr></thead><tbody>{rows}</tbody></table></div>{'<p class="notice">No course records extracted yet.</p>' if not courses else ''}</section>
<section id="sources" class="detail-section"><span class="eyebrow">05 / THE PAPER TRAIL</span><h2>Sources & provenance</h2><ol class="sources">{sources}</ol></section>'''
    return shell(p.get("title", "Program"), body, base)


def coverage_page(data, base):
    meta = data.get('meta', {})
    institutions = data.get('institutions', [])
    statuses = Counter(i.get('coverage_status') or 'pending' for i in institutions)
    identity_only = sum(p.get('curriculum_status') == 'pending' for p in data.get('programs', []))
    def coverage_evidence(i):
        links = [external(s.get('url'), s.get('title') or 'Inspection source') for s in i.get('coverage_sources', []) if isinstance(s, dict)]
        discoveries = [external(s.get('url'), s.get('title') or 'Program discovery') for s in i.get('discoveries', [])]
        return '<small>' + '<br>'.join(dict.fromkeys(links + discoveries)) + '</small>' if links or discoveries else ''

    def ranking_evidence(i):
        return '<br>'.join(external(r.get('source_url'), f"{r.get('category', 'Category unknown')} · #{r.get('rank', '?')} ({r.get('edition', '?')})") + '<small>' + esc(human(r.get('verification_status'))) + '</small>' for r in i.get('rankings', [])) or 'Not recorded'

    rows = ''.join(f'<tr><th scope="row">{external(i.get("website"), i.get("name"))}</th><td>{ranking_evidence(i)}</td><td>{badge(human(i.get("coverage_status") or "pending"))}</td><td>{esc(i.get("coverage_note") or "Inspection evidence not yet recorded.")}{coverage_evidence(i)}</td><td>{len(i.get("program_ids") or [])}</td></tr>' for i in sorted(institutions, key=lambda i: i.get('name', '')))
    cohort = meta.get('cohort') if isinstance(meta.get('cohort'), dict) else {}
    cohort_notes = ''.join(f'<li><strong>{esc(c.get("category"))}:</strong> {esc(c.get("note"))}</li>' for c in cohort.get('category_coverage', []))
    summary = meta.get('coverage_summary')
    summary = summary if isinstance(summary, str) else 'This atlas is a documented pilot. The listed institutions are not a complete ranking cohort.'
    body = f'''<section class="page-hero"><span class="eyebrow">THE BOUNDARIES OF THE EVIDENCE</span><h1>Coverage is part<br><em>of the finding.</em></h1><p class="lede">An absent record is not an absent program. This ledger makes the state of the research visible.</p></section><div class="notice"><strong>{esc(summary)}</strong><ul>{limitations(meta)}</ul></div>
<section class="detail-section"><h2>Recorded institutions</h2><p class="section-note">{len(institutions)} institution records · {len(data.get('programs', []))} documented programs. These are inventory counts, not a percentage of the intended cohort. {identity_only} records are identity-only with curriculum extraction pending; {len(data.get("programs", [])) - identity_only} have curriculum extraction in progress or complete. Counts include all documented records. Discovery links can identify additional programs awaiting a record.</p>{'<ul class="section-note">' + cohort_notes + '</ul>' if cohort_notes else ''}<div class="status-grid">{''.join('<div><strong>' + str(v) + '</strong><span>' + esc(human(k)) + '</span></div>' for k, v in sorted(statuses.items()))}</div><div class="table-scroll" role="region" aria-label="Institution coverage" tabindex="0"><table class="coverage-table"><thead><tr><th>Institution</th><th>Cohort membership</th><th>Research status</th><th>Evidence / remaining work</th><th>Documented records</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="detail-section prose"><h2>How to read a status</h2><dl class="definitions"><dt>Confirmed</dt><dd>An official source identifies a qualifying program. Curriculum extraction may still be partial.</dd><dt>No qualifying program found</dt><dd>A documented inspection of official catalogs and program directories found no qualifying title. This is a bounded search result, not proof of absence.</dd><dt>Inspected</dt><dd>Research has begun or sources have been inspected; use the evidence note for the precise conclusion.</dd><dt>Inaccessible</dt><dd>Required evidence could not be accessed. No conclusion about program existence follows.</dd><dt>Pending</dt><dd>Not yet inspected or no sufficient evidence recorded.</dd></dl><h2>The intended scope</h2><p>Two independent U.S. News cohorts: National Universities and National Liberal Arts Colleges ranked 100 or better, including ties. The latest edition and complete membership require source verification; a verified edition does not establish a complete institution roster. Program inclusion requires AI or Artificial Intelligence in the official undergraduate title.</p><p>Research generation: {esc(meta.get('generated_at') or 'Not recorded')}.</p><a href="{base}methodology/">Read the full methodology →</a></section>'''
    return shell('Coverage & limitations', body, base, 'coverage')


def methodology_page(data, base):
    meta = data.get('meta', {})
    cs = data.get('csrankings') or {}
    method = cs.get('methodology')
    research_config = ''
    if isinstance(method, dict):
        field_names = {'ai': 'Artificial intelligence', 'vision': 'Computer vision', 'mlmining': 'Machine learning & data mining', 'nlp': 'Natural language processing', 'inforet': 'Information retrieval'}
        fields = ', '.join(f'{field_names.get(field, field)} ({field})' for field in method.get('fields', [])) or 'Not configured'
        missingness = sorted({o.get('missingness') for o in cs.get('observations', []) if o.get('missingness')})
        settings = [
            ('Publication window', f"{method.get('year_start', 'Unknown')}–{method.get('year_end', 'Unknown')}"),
            ('Geographic filter', method.get('geographic_filter') or 'Not configured'),
            ('Research fields', fields),
            ('Pinned source snapshot', method.get('source_snapshot') or 'Not recorded'),
            ('Import status', method.get('status') or 'not_imported'),
            ('Recorded missingness', ', '.join(missingness) or 'No observation status recorded'),
        ]
        research_config = '<p>The following configuration is recorded for reproducibility. It has not been used to publish research values or ranks.</p><dl class="research-config">' + ''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>' for label, value in settings) + '</dl>'
        research_config += '<p>Null values and ranks remain unknown. The status “permission_required” means reuse permission is unresolved; it does not mean zero publications, no AI research, or an unranked institution.</p>'
        if method.get('source_url'):
            research_config += '<p>' + external(method['source_url'], 'Configured methodology source') + '</p>'
        for key in ('license_explanation', 'license_notes', 'missingness_explanation'):
            if method.get(key):
                research_config += f'<p>{esc(method[key])}</p>'
        method = method.get('method') or 'Publication-based research context; no values have been computed or redistributed.'
    elif not isinstance(method, str):
        method = 'CSRankings is a publication-based view of computer science research activity. Research context is distinct from undergraduate program quality.'
    body = f'''<section class="page-hero"><span class="eyebrow">HOW TO READ THE ATLAS</span><h1>Evidence before<br><em>inference.</em></h1><p class="lede">An inspectable research index. No composite scores, hidden rankings, or claims that a curriculum count measures quality.</p></section>
<div class="method-layout"><nav class="method-nav" aria-label="Methodology sections"><a href="#scope">01 · Scope</a><a href="#evidence">02 · Evidence</a><a href="#curriculum-method">03 · Curriculum</a><a href="#research">04 · Research context</a><a href="#unknowns">05 · Limitations</a></nav><div class="prose"><section id="scope"><h2>01 / A precise inclusion rule</h2><p>Programs qualify when their official undergraduate title includes AI or Artificial Intelligence. Degrees, additional majors, minors, and concentrations remain separate program types. A general computer science program with AI electives does not qualify on that basis alone.</p><p>The intended institution scope comprises two independent U.S. News top-100 cohorts, inclusive of ties: National Universities and National Liberal Arts Colleges. Until complete membership is source-verified and recorded, the atlas is a pilot inventory. Consult the coverage ledger for what has actually been inspected.</p></section>
<section id="evidence"><h2>02 / Follow the source</h2><p>Official university catalogs, program pages, and announcements support program records. Sources retain their URLs, retrieval dates, catalog years, locators, and confidence. The last verification date describes the research record, not a guarantee that the source has remained unchanged.</p><p>Launch dates are recorded only when evidence supports the date and its precision. The oldest search result is not treated as a program’s first offering. Source-stated learning outcomes and inferred editorial taxonomy appear in separate sections.</p></section>
<section id="curriculum-method"><h2>03 / Compare structure with care</h2><p>Requirements preserve all-of groups, course-count choices, credit-count choices, and nested alternatives. A course can belong to multiple requirements. The curriculum chart deduplicates courses by stable course ID and assigns each documented course to a single editorial category.</p><p>“Complete” describes the requirement inventory for the represented award at its recorded catalog year. A complete minor or concentration inventory does not cover the whole parent degree. Course descriptions, prerequisite statements, credit amounts, and known credit units have separate availability counts; a complete requirement inventory may still have missing course metadata.</p><p>Charts count observed course records. They do not measure required credit shares, course depth, teaching quality, or the student experience. Partial catalogs, elective pools, and different program sizes make these counts unsuitable for ranking programs.</p><p>Quarter hours, semester hours, course units, and other units retain their original labels. No conversion or normalized total is inferred. Unknown credits are null, never zero. Missing prerequisites, descriptions, course sites, or syllabi remain explicitly unrecorded.</p></section>
<section id="research"><h2>04 / Research is context</h2>{badge('CSRankings · not imported')}<p>{esc(method)}</p>{research_config}<p>CSRankings data and code have not been imported or redistributed because redistribution licensing remains unresolved for this project. No research score is attached to a program. Publication activity does not measure undergraduate teaching quality. Consult the original resource and its methodology directly.</p><p>{external('https://csrankings.org/', 'Visit CSRankings')} · {external('https://csrankings.org/faq', 'Read the CSRankings FAQ')}</p></section>
<section id="unknowns"><h2>05 / What remains unknown</h2><p>Coverage is incomplete. A missing institution or program does not establish absence. A “no qualifying program found” conclusion requires a documented search of official sources. Inaccessible pages remain inaccessible; pending institutions remain pending.</p><ul>{limitations(meta)}</ul><p>Use this atlas to frame questions, then confirm current admission and graduation requirements with the institution.</p><a href="{base}coverage/">Inspect the coverage ledger →</a></section></div></div>'''
    return shell('Methodology', body, base, 'methodology')


def build(data: dict, output: Path, base_path: str = '/ai-program-atlas/') -> None:
    """Write a portable static site. No network access or server is required."""
    base = '/' + base_path.strip('/') + '/' if base_path.strip('/') else '/'
    if not re.fullmatch(r'/[A-Za-z0-9_./-]*', base) or '..' in base:
        raise ValueError('base_path must be an absolute URL path without traversal')
    output = Path(output)
    programs = data.get('programs', [])
    for p in programs:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', p.get('id', '')):
            raise ValueError('Program IDs must be stable lowercase hyphenated slugs')
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    for asset in ('atlas.css', 'atlas.js'):
        shutil.copyfile(Path(__file__).parent / 'web' / asset, output / 'assets' / asset)
    pages = {'index.html': root_page(data, base), 'coverage/index.html': coverage_page(data, base), 'methodology/index.html': methodology_page(data, base)}
    for program in programs:
        pages[f'programs/{program["id"]}/index.html'] = program_page(program, base)
    for relative, content in pages.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    (output / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / '.nojekyll').touch()
