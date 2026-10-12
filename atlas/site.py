"""Dependency-free, escaped static publishing for the AI Program Atlas."""
from __future__ import annotations

from collections import Counter
from html import escape
import json
from hashlib import sha256
from pathlib import Path
import re
import shutil

from atlas.requirement_context import related_option_groups
from atlas.course_references import reference_matcher, referenced_courses
from atlas.curriculum_profile import requirement_profile
from atlas.awards import major_award_buckets
from atlas.rankings import institution_rank_context
from atlas.research_context import FIELDS as RESEARCH_FIELDS, institution_context, aggregate_rank_map

CATEGORIES = {
    "foundations": "Computing foundations", "mathematics": "Mathematics and Statistics",
    "ai_ml": "AI & machine learning", "systems": "Systems",
    "human_context": "Human context", "applications": "Domain studies & applications",
    "electives": "Electives", "other": "Other / unclassified",
}


def esc(value):
    return escape(str(value if value is not None else "Unknown"), quote=True)


def human(value):
    return str(value or "unknown").replace("_", " ").capitalize()


def ranking_label(rank):
    if rank.get("rank") is not None:
        return f"#{rank['rank']}"
    if rank.get("rank_upper_bound") is not None:
        return f"Top {rank['rank_upper_bound']} · exact rank unverified"
    return "Exact rank unverified"


def safe_url(value):
    value = str(value or "")
    return value if value.startswith(("https://", "http://")) else ""


def external(url, label):
    url = safe_url(url)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>' if url else esc(label)


def unique_courses(program):
    return list({c["id"]: c for c in program.get("courses", []) if c.get("id")}.values())


def course_profile(program):
    """Directory counts share the detail page's unique-course/source semantics."""
    courses = unique_courses(program)
    sources = {s.get('id'): s for s in program.get('sources', [])}
    metadata = {}
    for key in ('description', 'prerequisites', 'credits', 'credit_unit'):
        metadata[key] = sum(
            bool(safe_url(c.get('url')) or safe_url(sources.get(c.get('source_id'), {}).get('url')))
            and c.get(key) is not None and c.get(key) != ''
            and (key != 'credit_unit' or c.get(key) != 'unknown')
            for c in courses
        )
    return {
        'count': len(courses),
        'unknown_credits': sum(c.get('credits') is None for c in courses),
        'credit_units': list(dict.fromkeys(c.get('credit_unit') or 'unknown' for c in courses)),
        'categories': {key: sum((c.get('category') if c.get('category') in CATEGORIES else 'other') == key for c in courses) for key in CATEGORIES},
        'metadata': metadata,
    }


def directory_payload(data, base):
    """Project only directory/search/comparison fields; full evidence stays in data.json.

    This is a build-time view, not a second public data contract. Never mutate the
    SQLite export: detail pages still consume the complete requirement/course graph.
    """
    def fields(record, names):
        return {key: record[key] for key in names.split() if key in record}

    def ranking_fields(institution):
        return [fields(r, 'publisher edition category rank rank_upper_bound source_url verification_status') for r in institution.get('rankings', [])]

    family_map = {f['id']: f for f in data.get('families', [])}
    institution_map = {i['id']: i for i in data.get('institutions', [])}
    programs = []
    for original in data.get('programs', []):
        p = fields(original, 'id title program_kind award_level catalog_year last_verified verification_status curriculum_status')
        institution = original.get('institution', {})
        p['institution'] = fields(institution, 'id name calendar')
        p['cohort_group'] = program_cohort(original, institution_map)
        p['program_path'] = program_path(original)
        p['major_awards'] = major_filter_buckets(original)
        p['parent_context_html'] = parent_context_markup(original)
        p['major_context_html'] = major_relationship_markup(original)
        p['research_context'] = institution_context(data, institution.get('id'))
        p['award_options'] = [fields(option, 'label normalized source_id') for option in original.get('award_options', [])]
        if institution.get('rankings'):
            p['institution']['rankings'] = ranking_fields(institution)
        membership = original.get('family') or {}
        if membership:
            p['family'] = fields(membership, 'id variant_label disciplines relationship classification_kind')
            p['family']['requirement_overrides'] = [fields(change, 'shared_id operation reason source_id') for change in membership.get('requirement_overrides', [])]
        search_values = [original.get('title'), original.get('overview'), original.get('hosting_unit'), institution.get('name'), membership.get('variant_label'), family_map.get(membership.get('id'), {}).get('name'), *membership.get('disciplines', []), *institution.get('aliases', [])]
        search_values += [value for parent in original.get('parent_programs', []) for value in (parent.get('title'), parent.get('award_level'), parent.get('award_label'))]
        search_values += [value for c in unique_courses(original) for value in (c.get('name'), c.get('code'))]
        p['search_text'] = ' '.join(str(value) if value is not None else '' for value in search_values)
        p['course_profile'] = course_profile(original)
        p['curriculum_profile'] = curriculum_profile(original)
        # The comparison links to full nested evidence rather than embedding summaries twice.
        p['curriculum_profile']['choices'] = [fields(c, 'id title kind count credits credit_unit source_id parent_id origin context has_children') for c in p['curriculum_profile']['choices']]
        requirements = original.get('requirements', [])
        view_content = json.dumps([requirements, original.get('courses', []), original.get('sources', [])], sort_keys=True, ensure_ascii=False)
        p['requirement_view_key'] = sha256(view_content.encode()).hexdigest()[:12]
        parents = {r.get('parent_id') for r in requirements if r.get('parent_id')}
        # Lightweight family context stays in the directory. The comparison loads
        # its navigable requirement tree from the generated detail page on demand.
        p['requirements'] = []
        for requirement in requirements:
            is_root = not requirement.get('parent_id')
            is_local = bool(membership) and requirement.get('origin') in ('variant', 'replacement')
            if not (is_root or is_local):
                continue
            projected = fields(requirement, 'title')
            projected['is_root'] = is_root
            if is_root:
                projected.update(fields(requirement, 'kind'))
                if requirement.get('count') is not None:
                    projected['count'] = requirement['count']
                    projected['has_children'] = requirement.get('id') in parents
                if requirement.get('credits') is not None:
                    projected.update(fields(requirement, 'credits credit_unit'))
            if is_local:
                projected.update(fields(requirement, 'origin component summary source_id'))
            p['requirements'].append(projected)
        p['outcomes'] = [fields(o, 'text kind statement_type source_id') for o in original.get('outcomes', [])]
        p['links'] = [fields(link, 'url label kind') for link in original.get('links', [])]
        source_ids = {o.get('source_id') for o in p['award_options']} | {c.get('source_id') for c in p['curriculum_profile']['choices']} | {r.get('source_id') for r in p['requirements']} | {o.get('source_id') for o in p['outcomes']} | {c.get('source_id') for c in membership.get('requirement_overrides', [])}
        source_ids |= {r.get('source_id') for r in family_map.get(membership.get('id'), {}).get('shared_requirements', [])}
        p['sources'] = [fields(source, 'id url') for source in original.get('sources', []) if source.get('id') in source_ids]
        programs.append(p)
    institutions = []
    for original in data.get('institutions', []):
        institution = fields(original, 'id')
        institution['rankings'] = ranking_fields(original)
        institutions.append(institution)
    families = []
    for original in family_map.values():
        family = fields(original, 'id name classification_kind')
        family['shared_requirements'] = [fields(r, 'id title summary source_id') for r in original.get('shared_requirements', [])]
        ids = {r.get('source_id') for r in family['shared_requirements']}
        family['sources'] = [fields(s, 'id url') for s in original.get('sources', []) if s.get('id') in ids]
        families.append(family)
    return {'programs': programs, 'institutions': institutions, 'families': families, 'base_path': base, 'categories': CATEGORIES}


def asset_url(base, filename):
    digest = sha256((Path(__file__).parent / "web" / filename).read_bytes()).hexdigest()[:12]
    return f"{base}assets/{filename}?v={digest}"


def shell(title, body, base, current="", payload=None):
    current_attr = 'aria-current="page"'
    nav = "".join(f'<a {current_attr if current == key else ""} href="{base}{path}">{label}</a>' for key, path, label in [
        ("atlas", "", "Explore programs")])
    script = ""
    if payload is not None:
        serialized = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        script = f'<script id="atlas-data" type="application/json">{serialized}</script><script src="{asset_url(base, "atlas.js")}" defer></script>'
    if payload is not None or 'class="requirement-disclosure"' in body:
        script += f'<script src="{asset_url(base, "requirements.js")}" defer></script>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · AI Program Atlas</title><meta name="description" content="A source-backed field guide to undergraduate artificial intelligence programs, curricula, and research context.">
<link rel="stylesheet" href="{asset_url(base, "atlas.css")}"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="brand" href="{base}" aria-label="AI Program Atlas home"><span class="brand-mark" aria-hidden="true">A<span>I</span></span><span>AI Program Atlas<small>UNDERGRADUATE PROGRAM RESEARCH</small></span></a><nav aria-label="Main navigation">{nav}</nav></header>
<main id="main" tabindex="-1">{body}</main>
<footer><section class="method-callout footer-methods" aria-label="Sources and methods"><span class="eyebrow">SOURCES &amp; METHODS</span><h2>Check the evidence behind each record.</h2><p>Each program links to its sources and shows when it was checked. University statements about program aims and outcomes are kept separate from Atlas interpretations.</p><nav aria-label="Sources and methods links"><a {'aria-current="page"' if current == 'coverage' else ''} href="{base}coverage/">Coverage →</a><a {'aria-current="page"' if current == 'methodology' else ''} href="{base}methodology/">Methodology →</a><a {'aria-current="page"' if current == 'api' else ''} href="{base}api/">JSON API</a></nav></section><span>AI Program Atlas <span class="muted">/ An open research index</span></span><p>Programs change. Confirm requirements with the institution’s current official catalog.</p></footer>{script}</body></html>'''


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
        'partial': 'Partial means some requirements or their applicability remain unverified or unresolved.',
        'pending': 'Pending means program identity is documented; its requirement inventory has not yet been extracted.',
    }.get(p.get('curriculum_status'), 'Requirement inventory completeness has not been established.')
    return state + ' ' + scope + ' Course metadata completeness is assessed separately below. Listed electives and alternatives are options; every listed course is not necessarily required.'


def metadata_availability(p):
    courses = unique_courses(p)
    fields = [('description', 'Descriptions'), ('prerequisites', 'Prerequisite statements'), ('credits', 'Credit amounts'), ('credit_unit', 'Known credit units')]
    profile = course_profile(p)
    counts = [(label, profile['metadata'][key]) for key, label in fields]
    return '<section class="metadata-availability" aria-labelledby="metadata-title"><h3 id="metadata-title">Course metadata availability</h3><p class="section-note">Counts below show populated fields with a recorded course or source URL, across ' + str(len(courses)) + ' unique course records. They describe evidence availability, not requirement completeness. A missing prerequisite statement does not mean “no prerequisites”; an unknown credit unit cannot be converted or totaled.</p><dl class="metadata-counts">' + ''.join(f'<div><dt>{esc(label)}</dt><dd><strong>{count}</strong> of {len(courses)} sourced</dd></div>' for label, count in counts) + '</dl></section>'



def major_filter_buckets(program):
    return major_award_buckets(program)


def major_relationship_markup(program):
    relationship = program.get('major_relationship') or {}
    if relationship.get('kind') != 'second_major_only':
        return ''
    sources = {s['id']: s for s in program.get('sources', [])}
    evidence = ' · '.join(external(sources.get(sid, {}).get('url'), 'Source') for sid in relationship.get('source_ids', []))
    return '<div class="major-relationship"><p><strong>Second major only</strong> · ' + esc(relationship.get('official_term') or 'Official term not recorded') + '</p><details><summary>Eligibility &amp; source</summary><p>' + esc(relationship.get('eligibility') or 'Eligibility not yet recorded') + '</p><small>' + esc(relationship.get('locator') or '') + ' · ' + evidence + '</small></details></div>'


def parent_context_markup(program):
    if program.get('program_kind') != 'concentration':
        return ''
    parents = program.get('parent_programs') or []
    review = program.get('parent_program_review') or {}
    sources = {s['id']: s for s in program.get('sources', [])}
    if not parents:
        return '<div class="parent-programs"><strong>Parent program:</strong> Not yet verified' + ('<small>' + esc('; '.join(review.get('notes') or [])) + '</small>' if review.get('notes') else '') + '</div>'
    rows = []
    for parent in parents:
        award = parent.get('award_label') or parent.get('award_level') or 'Award not yet verified'
        if parent.get('award_label') and parent.get('award_level'):
            award += ' (' + parent['award_level'] + ')'
        evidence = ' · '.join(external(sources.get(sid, {}).get('url'), 'Source') for sid in parent.get('source_ids', []))
        detail = ('<p>' + esc(parent['eligibility']) + '</p>') if parent.get('eligibility') else ''
        rows.append('<li><strong>' + esc(parent.get('title')) + '</strong><span> · ' + esc(award) + '</span><small>' + esc(human(parent.get('relationship'))) + ' · ' + evidence + '</small>' + ('<details><summary>Parent eligibility &amp; evidence</summary>' + detail + '<small>' + esc(parent.get('locator') or 'Locator not recorded') + '</small></details>') + '</li>')
    status = 'Parent information partly verified.' if review.get('status') != 'verified' else ''
    notes = '; '.join(review.get('notes') or [])
    return '<div class="parent-programs"><strong>' + ('Parent program' if len(parents)==1 else 'Parent programs') + '</strong><ul>' + ''.join(rows) + '</ul>' + ('<small>' + esc(' '.join(x for x in [status, notes] if x)) + '</small>' if status or notes else '') + '</div>'


def award_options_markup(program):
    offered = program.get('award_options') or []
    if not offered:
        return ''
    sources = {s.get('id'): s for s in program.get('sources', [])}
    labels = ' · '.join(external(sources.get(option.get('source_id'), {}).get('url'), option['label']) for option in offered)
    return '<p class="award-options"><strong>Offered awards:</strong> ' + labels + '</p>'


def directory_sort_key(program, title=None, identity=None):
    rank = program.get('_research_rank')
    return (rank if rank is not None else float('inf'),
            str(program.get('institution', {}).get('name') or '').casefold(),
            str(title if title is not None else program.get('title') or '').casefold(),
            identity or program['id'])


def directory_sort_attributes(program, title=None, identity=None):
    rank, institution, title, identity = directory_sort_key(program, title, identity)
    return ' '.join(f'data-sort-{key}="{esc(value)}"' for key, value in [
        ('rank', program.get('_rank_context', {}).get('rank') or ''),
        ('csrankings', '' if rank == float('inf') else rank), ('institution', institution),
        ('title', title), ('id', identity)])


def directory_rank_markup(program, linked=True):
    context = program.get('_rank_context', {})
    rank = context.get('rank')
    label = f"#{rank}" if rank is not None else 'Exact rank unverified'
    details = f"U.S. News {context.get('edition') or 'edition unverified'} · {context.get('category') or 'Category unverified'}"
    evidence = human(context.get('verification_status'))
    if rank is None and context.get('reported_rank') is not None:
        evidence += f" · reported #{context['reported_rank']} is not used for sorting"
    if rank is None and context.get('reason'):
        evidence += ' · ' + str(context['reason']).replace('_', ' ')
    citation = external(context.get('source_url'), 'Ranking source') if linked and context.get('source_url') else ''
    research_rank = program.get('_research_rank')
    research_label = f'CSRankings AI aggregate · U.S. #{research_rank}' if research_rank is not None else 'CSRankings AI aggregate · rank unavailable'
    return '<span class="card-research-ranking">' + esc(research_label) + '</span><span class="card-ranking"><strong>' + esc(label) + '</strong> · ' + esc(details) + '<small>' + esc(evidence) + (' · ' + citation if citation else '') + '</small></span>'


def program_card(p, base):
    institution = p.get("institution", {})
    courses = unique_courses(p)
    variant = p.get("family") or {}
    variant_label = '<p class="variant-label">Variant: ' + esc(variant.get("variant_label") or p.get("title")) + '</p>' if variant else ''
    return f'''<article class="program-card" data-program-id="{esc(p['id'])}" {directory_sort_attributes(p)}>
<div class="card-top"><span class="eyebrow">{esc(institution.get('name'))}</span><span class="card-badges">{badge(human(p.get('program_kind')))}{badge(p.get('award_level')) if p.get('award_level') not in ('other', 'minor', 'concentration', None) else ''}</span></div>
<h3><a href="{base}programs/{esc(p['id'])}/">{esc(p.get('title'))}<span aria-hidden="true">↗</span></a></h3>
{directory_rank_markup(p)}{variant_label}{award_options_markup(p)}{major_relationship_markup(p)}{parent_context_markup(p)}<p class="card-description">{esc(p.get('overview') or 'Program overview has not yet been recorded.')}</p>
<dl class="card-facts"><div><dt>Academic calendar</dt><dd>{esc(human(institution.get('calendar')))}</dd></div><div><dt>Curriculum evidence</dt><dd>{esc(evidence_label(p))}</dd></div></dl>
<div class="card-evidence"><span>{len(courses)} course records</span><span>Verified {esc(date_value(p))}</span></div>
<div class="card-bottom"><a href="{base}programs/{esc(p['id'])}/">View program <span aria-hidden="true">→</span></a><label class="compare-choice js-only"><input type="checkbox" data-compare="{esc(p['id'])}"> Compare<span class="sr-only"> {esc(p.get('title'))} at {esc(institution.get('name'))}</span></label></div></article>'''


REQUIRED_COLUMNS = [('foundations', 'Computing'), ('mathematics', 'Mathematics and Statistics'), ('ai_ml', 'AIML'), ('systems', 'Systems'), ('human_context', 'Human Context'), ('applications', 'Applications'), ('other', 'Other')]


def directory_award_label(p):
    if p.get('program_kind') == 'additional_major':
        return '2ndMaj'
    return ' / '.join(option['label'] if len(option['label']) <= 12 else option['normalized'].upper() for option in p.get('award_options', [])) or (p.get('award_level') if p.get('award_level') != 'other' else 'Unspecified')


def directory_program_title(p):
    title = p.get('title') or 'Program title not recorded'
    labels = [option['label'] for option in p.get('award_options', [])] + [p.get('award_level'), 'Additional Major' if p.get('program_kind') == 'additional_major' else None]
    for label in labels:
        if label:
            variants = [label, {'BS':'B.S.', 'BA':'B.A.'}.get(label, label)]
            for text in variants:
                title = re.sub(r',\s*' + re.escape(text) + r'(?=\s*\(|\s*$)', '', title, flags=re.I)
    return title


def directory_parent_line(p):
    if p.get('program_kind') != 'concentration':
        return ''
    labels = []
    for parent in p.get('parent_programs', []):
        award = parent.get('award_level') or parent.get('award_label') or ''
        award = {'B.S.': 'BS', 'B.A.': 'BA', 'Bachelor of Science': 'BS', 'Bachelor of Arts': 'BA', 'Bachelor of Science in Engineering': 'BSE'}.get(award, award)
        labels.append(' '.join(value for value in [award, parent.get('title')] if value))
    return '<small class="directory-parent"><em>Parent: ' + esc('; '.join(labels) if labels else 'Not yet verified') + '</em></small>'


def required_directory_counts(p):
    if not unique_courses(p):
        return None
    categories = requirement_profile(p)['required_obligations']['categories']
    return {key: categories[key] + (categories.get('electives', 0) if key == 'other' else 0) for key, _ in REQUIRED_COLUMNS}


def northeastern_joint(p):
    # Display grouping is explicitly requested; it does not establish inheritance.
    return (p.get('family', {}).get('id') == 'northeastern-ai-combined-degrees' or p['id'] == 'northeastern-chemical-engineering-ai-bsche') and p.get('program_kind') == 'degree'


def table_program_group(p):
    # Only existing reviewed relationships authorize this presentation grouping.
    if northeastern_joint(p):
        return 'northeastern-joint-ai', 'Joint Artificial Intelligence programs', 'Northeastern joint'
    if (p.get('family', {}).get('id') == 'buffalo-ai-plus-x-degrees'
            and p.get('institution', {}).get('id') == 'university-at-buffalo-suny'
            and p.get('program_kind') == 'degree'):
        return 'buffalo-ai-plus-x', 'AI+X programs', 'Buffalo AI+X'
    return None


def program_table(programs, base):
    rows = []
    ordered = sorted(programs, key=directory_sort_key)
    emitted = set()
    for p in ordered:
        grouping = table_program_group(p)
        if grouping and grouping[0] not in emitted:
            group_id, group_title, group_label = grouping
            emitted.add(group_id)
            joint = [member for member in ordered if table_program_group(member) == grouping]
            profiles = [required_directory_counts(member) for member in joint]
            count_cells = ''
            for key, _ in REQUIRED_COLUMNS:
                values = [profile[key] for profile in profiles if profile is not None]
                label = str(min(values)) if values and min(values) == max(values) else str(min(values)) + '–' + str(max(values)) if values else '—'
                count_cells += '<td data-joint-count="' + key + '" class="required-count">' + label + '</td>'
            rows.append(f'''<tr class="directory-joint-group js-only" data-table-group="{group_id}" {directory_sort_attributes(p, group_title, group_id)}><td><button type="button" class="joint-compare" data-table-expand aria-label="Choose a {group_label} program to compare">＋</button></td><th scope="row">{esc(p.get('institution', {}).get('name'))}</th><td><button type="button" class="joint-toggle" data-table-expand aria-expanded="false">(<span class="joint-awards">{esc(' / '.join(sorted({directory_award_label(member) for member in joint})))}</span>) {esc(group_title)} <span class="joint-toggle-icon" aria-hidden="true">▸</span></button><small class="joint-summary">{len(joint)} programs · course-count ranges across variants</small></td><td>{esc('#' + str(p['_research_rank']) if p.get('_research_rank') is not None else '—')}</td><td>{external(p.get('_rank_context', {}).get('source_url'), '#' + str(p['_rank_context']['rank'])) if p.get('_rank_context', {}).get('rank') is not None else '—'}</td>{count_cells}</tr>''')
        rank = p.get('_research_rank')
        context = p.get('_rank_context', {})
        news_rank = context.get('rank')
        profile = required_directory_counts(p)
        count_cells = ''.join('<td class="required-count" data-required-category="' + key + '" title="Fixed courses plus countable required choices">' + (str(profile[key]) if profile is not None else '—') + '</td>' for key, _ in REQUIRED_COLUMNS)
        award_prefix = '' if p.get('program_kind') in {'concentration', 'minor'} else '<span class="directory-award">(' + esc(directory_award_label(p)) + ')</span> '
        group_attr = ' data-joint-member="' + grouping[0] + '"' if grouping else ''
        rows.append(f'''<tr data-row-id="{esc(p['id'])}"{group_attr} {directory_sort_attributes(p)}><td><label class="compare-choice js-only"><input type="checkbox" data-row-compare="{esc(p['id'])}"><span class="sr-only">Compare {esc(p.get('title'))} at {esc(p.get('institution', {}).get('name'))}</span></label></td><th scope="row">{esc(p.get('institution', {}).get('name'))}</th><td><a class="directory-program-link" href="{base}programs/{esc(p['id'])}/">{award_prefix}{esc(directory_program_title(p))}</a>{directory_parent_line(p)}</td><td>{esc('#' + str(rank) if rank is not None else '—')}</td><td>{external(context.get('source_url'), '#' + str(news_rank)) if news_rank is not None else '—'}</td>{count_cells}</tr>''')
    headers = '<th rowspan="2" scope="col"><span class="sr-only">Compare</span></th>' + ''.join('<th rowspan="2" scope="col">' + label + '</th>' for label in ['University', 'Program', '<a href="' + base + 'methodology/#research" title="CSRankings aggregate U.S. publication rank">AI Ranking</a>', 'US News Ranking']) + '<th colspan="7" scope="colgroup" class="required-heading">Required Curriculum</th>'
    return '<p class="directory-scroll-hint">Scroll the table to see rankings and required curriculum.</p><div class="directory-table-wrap table-scroll" role="region" aria-label="Program directory table" tabindex="0"><table class="directory-table"><colgroup><col style="width:50px"><col style="width:180px"><col style="width:320px"><col style="width:68px"><col style="width:82px"><col style="width:90px"><col style="width:90px"><col style="width:60px"><col style="width:76px"><col style="width:90px"><col style="width:94px"><col style="width:60px"></colgroup><caption class="sr-only">Required curriculum counts fixed courses plus countable mandatory selections, not credit loads or the whole degree. Joint-program ranges are not totals.</caption><thead><tr>' + headers + '</tr><tr>' + ''.join('<th scope="col">' + label + '</th>' for _, label in REQUIRED_COLUMNS) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


def family_group(family, members, base):
    sources = ' · '.join(external(source.get('url'), source.get('title') or 'Family source') for source in family.get('sources', []))
    shared = family.get('shared_requirements') or []
    shared_titles = ''.join('<li>' + esc(r.get('title')) + '</li>' for r in shared)
    codes = ', '.join(family.get('shared_course_codes') or [])
    classification = {'source_stated': 'Source-stated family', 'analyst_classified': 'Analyst-classified family'}.get(family.get('classification_kind'), 'Classification not recorded')
    return f'''<details class="program-family" data-family-id="{esc(family['id'])}" {directory_sort_attributes(members[0], family.get("name"), family["id"])}><summary><span class="family-heading"><span class="eyebrow">{esc(members[0].get('institution', {}).get('name'))}</span><strong>{esc(family.get('name'))}</strong>{directory_rank_markup(members[0], linked=False)}<span class="family-description">{esc(family.get('description') or 'Related programs with an explicitly documented family relationship.')}</span></span><span class="family-summary-meta">{badge(classification)}<span class="family-match-count">{len(members)} variants</span><span class="family-toggle">View variants</span></span></summary><div class="family-body"><div class="family-evidence"><p class="family-rank-source">{external(members[0].get("_rank_context", {}).get("source_url"), "Institution ranking source")}</p><p><strong>Shared structure; separate awards.</strong> Compare a concrete variant below. Family grouping does not combine awards or imply identical requirements.</p><details class="family-sources"><summary>Family evidence ({len(family.get('sources', []))} sources)</summary><p>{sources or 'Family sources not recorded.'}</p></details>{'<details class="shared-preview"><summary>Recorded shared requirements (' + str(len(shared)) + ' groups)</summary><ul>' + shared_titles + '</ul><p>Requirement groups include containers and choices; this is not a course total.</p></details>' if shared else '<p>Shared requirement structure has not yet been recorded.</p>'}{'<p><strong>Recorded shared course codes:</strong> ' + esc(codes) + '</p>' if codes else ''}</div><div class="family-variants">{''.join(program_card(program, base) for program in members)}</div></div></details>'''


def grouped_programs(programs, families, base):
    grouped = set()
    entries = []
    for family in families:
        members = sorted([p for p in programs if p.get('family', {}).get('id') == family.get('id') and p['id'] in family.get('variant_ids', [])], key=directory_sort_key)
        if not members:
            continue
        grouped.update(p['id'] for p in members)
        entries.append((directory_sort_key(members[0], family.get('name'), family['id']), family_group(family, members, base)))
    entries.extend((directory_sort_key(p), program_card(p, base)) for p in programs if p['id'] not in grouped)
    return ''.join(entry[1] for entry in sorted(entries, key=lambda entry: entry[0]))


def family_context(p, family, base):
    membership = p.get('family')
    if not membership:
        return ''
    sources = {source.get('id'): source for source in p.get('sources', [])}
    evidence = ' · '.join(external(sources[sid].get('url'), 'Relationship source') for sid in membership.get('source_ids', []) if sid in sources)
    sibling_links = ''.join(f'<li><a href="{base}programs/{esc(pid)}/">{esc(label)}</a></li>' for pid, label in (family or {}).get('_variant_labels', []) if pid != p['id'])
    shared = {r.get('id'): r for r in (family or {}).get('shared_requirements', [])}
    changes = ''.join('<li><strong>' + esc(human(change.get('operation'))) + ': ' + esc(shared.get(change.get('shared_id'), {}).get('title') or change.get('shared_id')) + '</strong> — ' + esc(change.get('reason') or 'Reason not recorded') + ' ' + external(sources.get(change.get('source_id'), {}).get('url'), 'Change source') + '</li>' for change in membership.get('requirement_overrides', []))
    label = 'Source stated' if membership.get('classification_kind') == 'source_stated' else 'Analyst classified' if membership.get('classification_kind') == 'analyst_classified' else 'Classification not recorded'
    family_label = {'source_stated': 'Source stated', 'analyst_classified': 'Analyst classified'}.get((family or {}).get('classification_kind'), 'Not recorded')
    relationship = {'ai_plus_x': 'AI + another discipline', 'x_plus_ai': 'Another discipline + AI', 'integrated': 'Integrated program', 'unknown': 'Relationship not recorded'}.get(membership.get('relationship'), 'Relationship not recorded')
    return f'''<section class="family-context" aria-labelledby="family-context-title"><div class="eyebrow">PROGRAM FAMILY</div><h2 id="family-context-title">{esc((family or {}).get('name') or membership.get('id'))}</h2><p><strong>{esc(membership.get('variant_label') or p.get('title'))}</strong> · {esc(relationship)}</p><p>Family grouping: {esc(family_label)}. Membership evidence: {esc(label)}.</p><p>Disciplines: {esc(', '.join(membership.get('disciplines') or []) or 'Not recorded')}. This page describes this concrete variant; shared and local variant requirement labels appear where documented. A local requirement is outside the recorded shared set; it is not necessarily unique to this variant.</p><p>{evidence}</p>{'<div class="family-changes"><h3>Changes to shared requirements</h3><ul>' + changes + '</ul></div>' if changes else ''}{'<details><summary>Other variants in this family</summary><ul>' + sibling_links + '</ul></details>' if sibling_links else ''}</section>'''


def limitations(meta):
    values = meta.get("limitations") or []
    if isinstance(values, str):
        values = [values]
    return "".join(f"<li>{esc(v)}</li>" for v in values)


def options(values):
    return "".join(f'<option value="{esc(key)}">{esc(label)}</option>' for key, label in values)


COHORT_GROUPS = {'nu': 'National Universities', 'lac': 'National Liberal Arts Colleges', 'unclassified': 'Institution category not established'}
PROGRAM_PATHS = {'majors': 'Majors', 'concentrations': 'Concentrations', 'minors': 'Minors'}


def program_path(program):
    return {'concentration': 'concentrations', 'minor': 'minors'}.get(program.get('program_kind'), 'majors')


def program_cohort(program, institutions):
    institution = institutions.get(program.get('institution', {}).get('id'), program.get('institution', {}))
    categories = {r.get('category') for r in institution.get('rankings', []) if r.get('category') in ('National Universities', 'National Liberal Arts Colleges')}
    if len(categories) != 1:
        return 'unclassified'
    return 'nu' if 'National Universities' in categories else 'lac'


def cohort_directory(programs, institutions, families, base, edition=None, csrankings=None):
    institution_map = {i['id']: i for i in institutions}
    research_ranks = aggregate_rank_map(csrankings or {})
    blocks = []
    for key, name in COHORT_GROUPS.items():
        members = [{**p, '_research_rank': research_ranks.get(p.get('institution', {}).get('id')), '_rank_context': institution_rank_context(institution_map.get(p.get('institution', {}).get('id'), p.get('institution', {})), name if key != 'unclassified' else None, edition)} for p in programs if program_cohort(p, institution_map) == key]
        if key == 'unclassified' and not members:
            continue
        tabs = []
        panels = []
        for path, label in PROGRAM_PATHS.items():
            entries = [p for p in members if program_path(p) == path]
            tabs.append(f'<button type="button" role="tab" id="tab-{key}-{path}" data-path="{path}" aria-controls="cohort-{key}-{path}" aria-selected="{"true" if path == "majors" else "false"}" tabindex="{0 if path == "majors" else -1}">{label} <span class="path-count">{len(entries)}</span></button>')
            panels.append(f'<div role="tabpanel" id="cohort-{key}-{path}" data-path="{path}" aria-labelledby="tab-{key}-{path}" tabindex="0"><h4 class="no-js-path-title">{label}</h4>{program_table(entries, base)}<div class="directory-cards"><div class="program-grid">{grouped_programs(entries, families, base)}</div></div><p class="cohort-empty" {"hidden" if entries else ""}>No {label.lower()} match the current filters in this institution category. This is not evidence that none exist.</p></div>')
        explanation = 'Category has not been resolved from recorded ranking evidence; institution names and program awards are not used to guess it.' if key == 'unclassified' else 'Grouped by recorded U.S. News institution category. Majors includes degrees and separately labeled additional majors.'
        blocks.append(f'<section class="cohort-directory" data-cohort-group="{key}" aria-labelledby="cohort-title-{key}"><div class="cohort-heading"><h3 id="cohort-title-{key}">{name}</h3><p class="cohort-result-count sr-only" role="status"></p></div><p class="cohort-explanation">{explanation}</p><div class="program-path-tabs js-only" role="tablist" aria-label="{name} program types">{"".join(tabs)}</div>{"".join(panels)}</section>')
    return '<div id="program-grid">' + ''.join(blocks) + '</div>'


def root_page(data, base):
    programs = data.get("programs", [])
    institutions = data.get("institutions", [])
    meta = data.get("meta", {})
    families = data.get("families") or []
    variants = [p for p in programs if p.get("family")]
    discipline_values = sorted({d for p in variants for d in p["family"].get("disciplines", [])})
    cohort = meta.get("cohort")
    filters = [
        ("type", "Program type", [("degree", "Degree"), ("additional_major", "Additional major"), ("minor", "Minor"), ("concentration", "Concentration")]),
        ("award", "Award", sorted({(p.get("award_level", "other"), p.get("award_level", "Other")) for p in programs})),
        ("evidence", "Curriculum evidence", [("pending", "Pending — identity only"), ("partial", "Partial requirements"), ("complete", "Complete requirements")]),
        ("calendar", "Calendar", sorted({(p.get("institution", {}).get("calendar") or "unknown", human(p.get("institution", {}).get("calendar"))) for p in programs})),
        ("institution", "Institution", sorted({(p.get("institution", {}).get("id", ""), p.get("institution", {}).get("name", "Unknown")) for p in programs}, key=lambda v: v[1])),
        ("cohort", "Institution category", [("National Universities", "National Universities"), ("National Liberal Arts Colleges", "National Liberal Arts Colleges")]),
        ("category", "Course category", list(CATEGORIES.items())),
        ("discipline", "Family discipline", [(d, d) for d in discipline_values]),
    ]
    controls = "".join(f'<label for="filter-{key}">{label}<select id="filter-{key}" name="{key}"><option value="">All</option>{options(vals)}</select></label>' for key, label, vals in filters)
    institution_map = {i['id']: i for i in institutions}
    for group, name in COHORT_GROUPS.items():
        members = [p for p in programs if program_cohort(p, institution_map) == group]
        if group == 'unclassified' and not members:
            continue
        award_values = [('', 'All awards'), ('BS', 'BS'), ('BSE', 'BSE'), ('BA', 'BA'), ('second_major', 'Second majors'), ('other', 'Other / unspecified')]
        controls += '<label for="major-award-' + group + '">' + name + ' major award<select id="major-award-' + group + '" data-major-award data-award-group="' + group + '">' + options(award_values) + '</select></label>'
    body = f'''<h1 class="sr-only">Program directory</h1>
<section class="explorer directory-explorer" aria-labelledby="explore-title"><h2 id="explore-title" class="sr-only">Find a program</h2>
<div class="directory-toolbar js-only"><button type="button" id="open-filters" aria-haspopup="dialog" aria-controls="filter-panel">Search &amp; filters</button><span id="active-filter-summary" role="status" aria-live="polite">No search filters active</span><label class="sort-control" for="sort-order"><span class="sr-only">Sort programs</span><select id="sort-order" name="sort"><option value="csrankings">AI Ranking</option><option value="rank">U.S. News rank · ascending</option><option value="name">Institution name · A–Z</option></select></label></div>
<dialog id="filter-panel" class="filter-dialog" aria-labelledby="filter-title"><div class="dialog-heading"><h2 id="filter-title">Search &amp; filters</h2><button type="button" id="close-filters" aria-label="Close search and filters">Close</button></div><form id="filters" class="filters" role="search"><label class="search-label" for="search">Search programs<input type="search" id="search" name="q" placeholder="Institution, program, or course…" autocomplete="off"></label><div class="filter-row">{controls}</div><div class="filter-footer"><p class="filter-help">Course categories include elective options. Discipline filters use reviewed family membership. Exact awards and second-major eligibility are source verified; multiple offered awards count as one program.</p><button type="button" id="reset-filters" class="text-button">Reset filters</button></div><button type="button" id="apply-filters">Show results</button></form></dialog>
<noscript><p class="notice">All documented programs are listed below. Enable JavaScript to filter and compare programs.</p></noscript>
<p id="result-count" class="sr-only" role="status" aria-live="polite">{len(programs)} programs</p>
{cohort_directory(programs, institutions, families, base, cohort.get('edition') if isinstance(cohort, dict) else None, data.get('csrankings'))}<p class="directory-method-note">Required Curriculum counts fixed courses plus mandatory choose-N selections with a clear category and no unresolved overlap. A choose-one block counts as one course, not its option-pool size. Credit-only, nested, mixed-category and overlapping choices remain separate; incomplete inventories can omit courses, and 0 means none mapped. Other includes unclassified and generic elective categories. Joint-program ranges reflect matching variants, not a combined curriculum. Missing inventories and ranks use —. AI Ranking is the CSRankings five-field aggregate U.S. publication rank. <a href="{base}methodology/#research">Ranking methodology</a> · <a href="{base}coverage/">Coverage and limitations</a></p>
<div id="empty-state" class="empty-state" hidden><span class="eyebrow">NO MATCHES</span><h3>No programs match your filters.</h3><p>No documented program matches these filters. This does not establish that such a program does not exist.</p><button type="button" id="empty-reset">Clear filters</button></div></section>
<div id="compare-tray" class="compare-tray" hidden><span id="tray-count">0 of 4 selected</span><a href="#comparison">Compare programs ↓</a></div><section id="comparison" class="comparison js-only" aria-labelledby="compare-title"><div class="section-heading"><div><span class="eyebrow">PROGRAM COMPARISON</span><h2 id="compare-title">Compare programs</h2></div><button type="button" id="clear-comparison" class="text-button">Clear selection</button></div><p class="comparison-intro">Choose up to four programs. Credit units and incomplete curricula stay visible; course counts are not measures of program quality.</p><label class="comparison-profile-control" for="compare-profile">Curriculum profile<select id="compare-profile"><option value="required">Required curriculum</option><option value="options">Elective options</option></select></label><div id="compare-status" role="status" aria-live="polite"></div><div id="comparison-content"><p class="comparison-placeholder">Select “Compare” on a program to begin.</p></div></section>
'''
    return shell("Explore undergraduate AI programs", body, base, "atlas", directory_payload(data, base))


def curriculum_profile(program):
    """Decorate the resolved-graph profile with presentation-only choice context."""
    profile = requirement_profile(program)
    parents = {r.get('parent_id') for r in program.get('requirements', []) if r.get('parent_id')}
    profile['choices'] = [dict(choice, has_children=choice.get('id') in parents) for choice in profile['choices']]
    return profile


def profile_selection(choice):
    parts = []
    if choice.get('count') is not None:
        noun = 'alternative' if choice.get('kind') == 'alternative' else 'selection' if choice.get('has_children') else 'course'
        parts.append(f"Choose {choice['count']:g} {noun}" + ('' if choice['count'] == 1 else 's'))
    elif choice.get('kind') == 'alternative':
        parts.append('Choose an alternative')
    if choice.get('credits') is not None:
        parts.append(f"{choice['credits']:g} {human(choice.get('credit_unit'))} recorded")
    return ' · '.join(parts) or 'Selection amount not recorded'


def profile_choices(program, profile):
    choices = profile['choices']
    if not choices:
        return '<p class="profile-unavailable">No structured course or credit selection rules are recorded. See the full requirements for notes and unresolved rules.</p>'
    sources = {s.get('id'): s for s in program.get('sources', [])}
    contexts = {'required': 'Required selection', 'conditional': 'Conditional selection', 'unresolved': 'Selection context unresolved'}
    items = []
    counted = {c["id"]: c for c in profile["required_obligations"]["counted_choices"]}
    excluded = {c["id"]: c["reason"] for c in profile["required_obligations"]["excluded_choices"]}
    for choice in choices:
        context = contexts.get(choice.get('context'), 'Selection context unresolved')
        origin = {'family': 'Shared family requirement', 'variant': 'Local variant requirement', 'replacement': 'Variant replacement'}.get(choice.get('origin'))
        accounting = "Counts as {} required {} selection(s).".format(counted[choice["id"]]["count"], CATEGORIES[counted[choice["id"]]["category"]]) if choice["id"] in counted else "Not added to counts: " + excluded.get(choice["id"], "context unresolved") + "."
        items.append(f'<li><small>{esc(accounting)}</small><strong>{esc(choice.get("title"))}</strong><div class="profile-choice-rule">{esc(profile_selection(choice))}</div><small>{esc(context)}{esc(" · " + origin) if origin else ""}. Nested rules are not added together.</small>{"<p>" + esc(choice["summary"]) + "</p>" if choice.get("summary") else ""}<small>{external(sources.get(choice.get("source_id"), {}).get("url"), "Source")} · <a href="#requirement-{esc(choice.get("id"))}">Full requirement</a></small></li>')
    return f'<details class="profile-choices"><summary>{len(choices)} documented selection rules</summary><p class="profile-denominator">Course counts and credit amounts are different measures. Each rule retains its own unit and parent context; no pathway is selected for you.</p><ul>{"".join(items)}</ul></details>'


def category_count_label(count):
    return str(count) if count else '0 mapped'


def taxonomy_coverage_note(group):
    coverage = group.get('classification') or dict(reviewed=0, mixed=0, unclassified=0, unreviewed=group['count'])
    return (f"Taxonomy review: {coverage['reviewed']} reviewed · {coverage['mixed']} mixed · "
            f"{coverage['unclassified']} unclassified · {coverage['unreviewed']} unreviewed, "
            f"of {group['count']} mapped identities. Missing review is not verified classification. "
            "Requirement inventory completeness is separate.")


def profile_identity_note(profile, group):
    identity = profile.get('identity') or {}
    if not identity.get('crosslisted_aliases'):
        return ''
    records = group.get('source_record_count', group['count'])
    return (f"{group['count']} mapped course identities from {records} retained source-code records in this view. "
            "Only explicitly verified cross-lists are combined. The course table retains every source code and its evidence.")


def course_identity_evidence(p):
    groups = p.get('course_identity_groups') or []
    if not groups:
        return ''
    courses = {c['id']: c for c in p.get('courses', [])}
    sources = {s['id']: s for s in p.get('sources', [])}
    rows = []
    for group in groups:
        codes = ' / '.join(courses.get(cid, {}).get('code') or cid for cid in group['course_ids'])
        links = ' · '.join(external(sources.get(sid, {}).get('url'), 'Source') for sid in group['source_ids'])
        rows.append('<li><strong>' + esc(codes) + '</strong> — one course identity.<p>' + esc(group['rationale']) + '</p><small>' + esc(group['locator']) + ' · ' + links + '</small></li>')
    return '<details class="profile-identities"><summary>Verified cross-list identities (' + str(len(groups)) + ' groups)</summary><ul>' + ''.join(rows) + '</ul></details>'


def category_chart(p):
    courses = unique_courses(p)
    if not courses:
        return '<div class="notice"><strong>Curriculum profile not yet extracted.</strong><p>No course records are available for this program. Category coverage is unknown; missing records do not mean the curriculum contains zero courses in a category.</p></div>'
    profile = curriculum_profile(p)
    panels = []
    for mode, label in [('required', 'required course obligation'), ('options', 'elective option')]:
        group = profile[mode]
        plotted = profile['required_obligations'] if mode == 'required' else group
        total = plotted['count']
        identity_note = profile_identity_note(profile, group)
        count_noun = 'identities' if identity_note else 'records'
        identity_markup = '<p class="profile-identity">' + esc(identity_note) + '</p>' if identity_note else ''
        description = f"{group['count']} distinct fixed required course {count_noun} + {profile['required_obligations']['choice_count']} mandatory course selections. Countable choose-N blocks contribute N, not pool size. Credit-only, nested, mixed-category and overlapping rules remain separate below; source conditions still apply." if mode == 'required' else 'Available elective and required-choice options, not courses every student must take. Fixed required courses are excluded from this option count.'
        chart = ''
        if total:
            maximum = max(plotted['categories'].values()) or 1
            chart = '<div class="category-chart">' + ''.join(f'<div class="category-row" data-category="{key}"><span>{name}</span><div class="bar-track" aria-hidden="true"><span class="bar" style="width:{plotted["categories"].get(key, 0) / maximum * 100:.2f}%"></span></div><strong>{category_count_label(plotted["categories"].get(key, 0))}</strong></div>' for key, name in CATEGORIES.items()) + '</div>'
        else:
            chart = '<p class="profile-unavailable">' + ('A fixed required course set is not established by the recorded rules. This does not mean there are no requirements.' if mode == 'required' else 'No elective option set is established by the recorded structured rules.') + '</p>'
        panels.append(f'<div class="profile-panel" data-profile="{mode}"><p class="profile-total">{str(total) + " required course obligations" if mode == "required" else str(total) + " distinct elective option " + count_noun}</p><p class="profile-denominator">{description}</p>{identity_markup}<p class="profile-taxonomy">{esc(taxonomy_coverage_note(group))}</p>{chart}</div>')
    uncertainty_noun = 'course identities' if profile.get('identity', {}).get('crosslisted_aliases') else 'course records'
    outside_count = profile["unresolved"]["count"]
    outside_noun = ('course identity' if profile.get('identity', {}).get('crosslisted_aliases') else 'course record') if outside_count == 1 else uncertainty_noun
    uncertainty = f'{outside_count} {outside_noun} {"is" if outside_count == 1 else "are"} outside the fixed/option count profiles; see individual requirement rules for their context.'
    if profile['unresolved_group_count']:
        uncertainty += f' {profile["unresolved_group_count"]} groups need their full recorded context.'
    if profile['overlap_count']:
        uncertainty += f' {profile["overlap_count"]} {uncertainty_noun} appear in multiple groups and are counted once.'
    return '<div class="curriculum-profile"><p class="profile-denominator">Required counts include fixed mapped course identities plus countable mandatory selections. Option counts show distinct candidate identities. These are not credit totals or shares of the degree. Categories describe mapped records, including Other / unclassified. “0 mapped” means no mapped records classified in that category in this view—not evidence that the curriculum lacks that subject. Partial requirement or taxonomy evidence can omit relevant courses.</p><fieldset class="profile-switch"><legend>Curriculum view</legend><input class="sr-only" type="radio" name="curriculum-view" id="profile-required" value="required" checked><label for="profile-required">Required curriculum</label><input class="sr-only" type="radio" name="curriculum-view" id="profile-options" value="options"><label for="profile-options">Elective options</label><div class="profile-panels">' + ''.join(panels) + '</div></fieldset><p class="profile-uncertainty">' + esc(uncertainty) + '</p>' + course_identity_evidence(p) + profile_choices(p, profile) + '</div>'

def requirement_tree(p, base="", matcher=None):
    matcher = matcher if matcher is not None else reference_matcher(dict(p, id=p.get("id", "program")))
    requirements = p.get("requirements", [])
    course_map = {c["id"]: c for c in unique_courses(p)}
    ids = {r.get("id") for r in requirements}
    sources = {s.get('id'): s for s in p.get('sources', [])}
    children_by_id = {}
    for r in requirements:
        children_by_id.setdefault(r.get('parent_id'), []).append(r)
    rendered = set()
    course_branches = {}
    related_groups = related_option_groups(requirements)
    indexed_group_ids = {g['id'] for groups in related_groups.values() for g in groups}

    def has_courses(r, seen=frozenset()):
        rid = r.get('id')
        if rid in seen:
            return False
        if rid not in course_branches:
            course_branches[rid] = ((r.get('kind') != 'note' and bool(r.get('course_ids'))) or r.get('kind') in {'choose_courses', 'choose_credits', 'alternative'} or any(has_courses(child, seen | {rid}) for child in children_by_id.get(rid, [])))
        return course_branches[rid]

    def optional(r):
        return bool(re.match(r'^\s*optional\b', r.get('title') or '', re.I))

    def general_education(r):
        # Only explicit source/title labels establish institution-wide scope.
        title = (r.get('title') or '').strip()
        source_title = (sources.get(r.get('source_id'), {}).get('title') or '').strip()
        # A major described as excluding/beyond general education is program scope.
        if re.search(r'\b(?:excluding|beyond|outside|not including)\b.*(?:general education|\bGIRs?\b)', title, re.I):
            return False
        scope_heading = r'^(?:(?:unified|engineering|university|college|institution(?:-wide)?|institute)\s+)*general\s+(?:education|institute\s+requirements)\b'
        return bool(re.search(scope_heading, title, re.I) or re.search(scope_heading, source_title, re.I) or re.search(r'\(\s*GIRs?\s*\)', title, re.I))

    def course_title(c):
        return (c.get('name') or 'Course name not verified') + (' (' + c['code'] + ')' if c.get('code') else '')

    def redundant_wrapper(r, parent):
        """Only source-equivalent all-of labels with no additional policy flatten."""
        title = (r.get('title') or '').strip()
        generic = bool(re.match(r'^all (?:of )?(?:the )?following\b', title, re.IGNORECASE))
        numbered = re.fullmatch(r'\((\d+) courses?\)', title, re.IGNORECASE)
        generic = generic or bool(numbered and int(numbered[1]) == len(set(r.get('course_ids') or [])) and not children_by_id.get(r.get('id')))
        duplicate = title.casefold() == (parent.get('title') or '').strip().casefold()
        return (parent.get('kind') == r.get('kind') == 'all'
                and r.get('source_id') in sources and bool(r.get('source_id'))
                and r.get('source_id') == parent.get('source_id')
                and all(cid in course_map for cid in r.get('course_ids') or [])
                and (generic or duplicate) and r.get('count') is None
                and r.get('credits') is None and not r.get('source_text')
                and not r.get('origin') and not r.get('component')
                and (not r.get('summary') or r['summary'].strip() == title)
                and not optional(r) and not general_education(r))

    def course_rows(courses, required_credits='', scope_id='', evidence=''):
        rows = []
        for c in courses:
            amount = c.get('credits')
            if isinstance(amount, (float, int)) and amount == int(amount):
                amount = int(amount)
            unit = human(c.get('credit_unit')) if c.get('credit_unit') not in (None, 'unknown') else 'credit unit unknown'
            credits = f'{amount} {unit}' if amount is not None else ''
            title = (c.get('code') or 'Code unknown') + ' · ' + (c.get('name') or 'Course name not verified')
            course_evidence = external(c.get('url'), 'Course source') if c.get('url') else 'Course source not recorded.'
            prerequisites = prerequisite_markup(c, matcher, p.get('id', 'program'), base) if c.get('prerequisites') else '<p>Not recorded; this does not mean there are no prerequisites.</p>'
            rows.append('<li class="requirement-course-row" id="requirement-course-' + esc(scope_id) + '-' + esc(c['id']) + '"><details class="requirement-course-details" data-course-id="' + esc(c['id']) + '"><summary><span class="requirement-course-name">' + esc(title) + '</span><span class="requirement-course-credits">' + esc(credits) + '</span>' + ('<span class="requirement-course-source">' + evidence + '</span>' if evidence else '') + '</summary><div class="requirement-course-info"><p>' + esc(c.get('description') or 'Description not recorded.') + '</p><div class="requirement-prerequisites"><strong>Prerequisites: </strong>' + prerequisites + '</div>' + ('<p>Requirement credit amount: ' + esc(required_credits) + '</p>' if required_credits else '') + '<p><a href="#course-' + esc(c['id']) + '">Full course record</a> · ' + course_evidence + '</p></div></details></li>')
        return '<ul class="requirement-course-rows">' + ''.join(rows) + '</ul>' if rows else ''

    def bundle(title, members, seen, depth, key):
        if not members:
            return ''
        content = ''.join(render(r, seen, depth) for r in members)
        return '<li class="requirement-bundle" id="requirements-group-' + esc(key) + '"><details class="requirement-bundle-disclosure"><summary><h3>' + esc(title) + '</h3><span class="requirement-rule">' + str(len(members)) + ' recorded ' + ('branch' if len(members) == 1 else 'branches') + ' · expand to inspect</span></summary><ul>' + content + '</ul></details></li>'

    def render_level(nodes, seen, depth, root=False, parent='top', scope=None):
        main, notes, other, options, general = [], [], [], [], []
        for r in nodes:
            if r.get('id') in seen or r.get('id') in rendered:
                continue
            if optional(r):
                options.append(r)
            elif root and has_courses(r) and general_education(r):
                general.append(r)
            elif root and not has_courses(r):
                other.append(r)
            elif not has_courses(r):
                notes.append(r)
            else:
                main.append(r)
        main.sort(key=lambda r: (general_education(r), r.get('kind') == 'note'))
        return ''.join(render(r, seen, depth, scope) for r in main) + bundle('General education requirements', general, seen, depth, 'general-' + parent) + bundle('Optional concentrations & fields', options, seen, depth, 'optional-' + parent) + bundle('Requirement notes', notes, seen, depth, 'notes-' + parent) + bundle('Other requirements', other, seen, depth, 'other-' + parent)

    def related_markup(r, depth):
        groups = related_groups.get(r['id'], [])
        if not groups:
            return ''
        panels = []
        for group in groups:
            rows = []
            for child in children_by_id.get(group['id'], []):
                courses = [course_map[cid] for cid in dict.fromkeys(child.get('course_ids') or []) if cid in course_map]
                conjunction = '<span class="related-route-rule">All ' + str(len(courses)) + ' courses in this option (AND)</span>' if len(courses) > 1 else ''
                rows.append('<li class="related-option-route">' + conjunction + course_rows(courses, scope_id='reading-' + r['id'] + '-' + child['id']) + '</li>')
            panels.append('<details ' + ('open' if depth + 1 < 2 else '') + ' id="requirement-reading-' + esc(r['id']) + '-' + esc(group['id']) + '" class="related-course-group" data-related-requirement="' + esc(group['id']) + '"><summary><h4>' + esc(re.sub(r'\s+designation overlay$', '', group.get('title') or 'Course grouping')) + '</h4><span>' + str(len(rows)) + ' option routes</span><span class="related-group-rule">' + esc(group.get('summary') or 'Group rule has not been extracted; consult the recorded context.') + '</span></summary><ul class="related-option-routes">' + ''.join(rows) + '</ul><a class="related-group-context" href="#requirement-' + esc(group['id']) + '">Full recorded context →</a></details>')
        return '<section class="related-course-groups" data-related-pool="' + esc(r['id']) + '"><h4>Area / course groupings</h4><p>These same-source groups share complete option routes with this pool. Membership can overlap; this reading view adds no required slots. Follow each recorded group rule.</p>' + ''.join(panels) + '</section>'

    def render(r, seen, depth=0, scope=None):
        rid = r.get('id')
        if rid in seen or rid in rendered:
            return ''
        seen = seen | {rid}
        rendered.add(rid)
        courses = [course_map[cid] for cid in dict.fromkeys(r.get('course_ids') or []) if cid in course_map]
        child_nodes = children_by_id.get(rid, [])
        flatten = bool(scope and redundant_wrapper(r, scope))
        children = render_level(child_nodes, seen, depth if flatten else depth + 1, parent=rid, scope=r)
        child_markup = '<ul>' + children + '</ul>' if children else ''
        complete_courses = len(courses) == len(set(r.get('course_ids') or []))
        # Canonical anchor survives even when a display-only wrapper disappears.
        if flatten:
            return '<li class="requirement requirement-flattened" id="requirement-' + esc(rid) + '" data-requirement-depth="' + str(depth) + '">' + course_rows(courses, scope_id=rid) + child_markup + '</li>'
        source = sources.get(r.get('source_id'), {})
        inherited_source = scope and scope.get('source_id') == r.get('source_id') and bool(source)
        evidence = '' if inherited_source else '<span class="requirement-evidence">' + (external(source.get('url'), 'Requirement source') if source else 'Requirement source not recorded.') + '</span>'
        credits = ''
        if r.get('credits') is not None:
            amount = r['credits']
            if isinstance(amount, (float, int)) and amount == int(amount):
                amount = int(amount)
            credits = str(amount) + ' ' + (human(r.get('credit_unit')) if r.get('credit_unit') not in (None, 'unknown') else 'credit unit unknown')
        kind = r.get('kind')
        title = (r.get('title') or 'Untitled group').strip()
        summary_text = (r.get('summary') or '').strip()
        if summary_text.casefold().rstrip('.') == title.casefold().rstrip('.'):
            summary_text = ''
        count = r.get('count')
        if kind == 'all':
            flat_courses = list(courses)
            flat_children = list(child_nodes)
            while len(flat_children) == 1 and redundant_wrapper(flat_children[0], r):
                child = flat_children[0]
                flat_courses.extend(course_map[cid] for cid in dict.fromkeys(child.get('course_ids') or []) if cid in course_map)
                flat_children = children_by_id.get(child['id'], [])
            if flat_courses and not flat_children and complete_courses:
                n = len({c['id'] for c in flat_courses})
                rule = 'All ' + str(n) + ' courses required' if n > 1 else 'Required course'
                if scope and scope.get('kind') in ('alternative', 'choose_courses') and n > 1:
                    rule += ' (AND)'
            else:
                rule = 'All groups required (AND)' if child_nodes else 'Complete all listed courses' if courses else 'Complete all recorded items'
            if count is not None:
                rule += ' · ' + str(count) + ' recorded courses'
        elif kind == 'alternative':
            rule = ('Complete one route (OR)' if count in (None, 1) else 'Choose ' + str(count) + ' routes (OR)')
        elif kind == 'choose_courses':
            noun = 'option' if child_nodes else 'course'
            rule = 'Choose ' + str(count) + ' ' + noun + ('' if count == 1 else 's') if count is not None else 'Choose ' + noun + 's · count not recorded'
        elif kind == 'choose_credits':
            rule = 'Choose courses totaling ' + credits if credits else 'Choose by credit amount · amount not recorded'
        else:
            rule = summary_text or ('Course grouping / context' if has_courses(r) else 'Requirement note')
            if kind == 'note' and has_courses(r):
                summary_text = ''
        if credits and kind != 'choose_credits':
            rule += ' · ' + credits
        identities = {str(c.get(k) or '').strip().casefold() for c in courses for k in ('code', 'name')}
        single_identity = (kind == 'all' and len(courses) == 1 and complete_courses and not child_nodes
                           and (title.casefold() in identities or bool(re.fullmatch(r'(?:first|second|alternative) course route', title, re.IGNORECASE))) and count in (None, 1)
                           and not r.get('origin') and not r.get('component')
                           and (r.get('credits') is None or (r.get('credits') == courses[0].get('credits')
                                and r.get('credit_unit') == courses[0].get('credit_unit'))))
        if single_identity and summary_text.casefold().rstrip('.') in {x.rstrip('.') for x in identities}:
            summary_text = ''
        origin = {'family': 'Shared family requirement', 'variant': 'Local variant requirement', 'replacement': 'Variant replacement'}.get(r.get('origin'))
        tags = badge(origin) if origin else ''
        if r.get('component') in ('ai_core', 'domain', 'integration'):
            tags += badge({'ai_core': 'AI core', 'domain': 'Discipline', 'integration': 'Integration'}[r['component']])
        notes = '<details class="requirement-support"><summary>Requirement notes</summary><p>' + esc(summary_text) + '</p></details>' if summary_text else ''
        wording = '<details class="source-wording"><summary>Source wording</summary><blockquote>' + esc(r['source_text']) + '</blockquote></details>' if r.get('source_text') else ''
        unknown_ids = [cid for cid in r.get('course_ids') or [] if cid not in course_map]
        missing = '<p class="notice">Course records not available: ' + esc(', '.join(unknown_ids)) + '</p>' if unknown_ids else ''
        related = related_markup(r, depth)
        if related and child_markup:
            child_markup = '<details id="requirement-pool-' + esc(rid) + '" class="requirement-option-pool"><summary>All published option routes (' + str(len(child_nodes)) + ')</summary>' + child_markup + '</details>'
        content = ('<div class="requirement-tags">' + tags + '</div>' if tags else '') + notes + wording + related + course_rows(courses, credits if single_identity else '', rid, evidence if single_identity else '') + missing + child_markup
        if single_identity:
            route_label = '<h4 class="requirement-route-label">' + esc(title) + '</h4>' if title.casefold() not in identities else ''
            return '<li class="requirement requirement-single-course" id="requirement-' + esc(rid) + '" data-requirement-depth="' + str(depth) + '">' + route_label + content + '</li>'
        code_bundle = ' + '.join(c.get('code') or '' for c in courses)
        if len(courses) > 1 and title == code_bundle:
            title = 'Course bundle'
        elif len(courses) == 1 and title.casefold() in identities and not single_identity:
            title = 'Course requirement'
        opened = (depth < 2 and has_courses(r) and not optional(r) and not general_education(r)
                  and (kind != 'note' or depth > 0) and rid not in indexed_group_ids)
        return '<li class="requirement" id="requirement-' + esc(rid) + '" data-requirement-depth="' + str(depth) + '"><details class="requirement-disclosure" ' + ('open' if opened else '') + '><summary><span class="requirement-header-links">' + evidence + '</span><h3 class="requirement-title">' + esc(title) + '</h3><span class="requirement-rule">' + esc(rule) + '</span></summary><div class="requirement-body">' + content + '</div></details></li>'

    roots = [r for r in requirements if not r.get("parent_id") or r.get("parent_id") not in ids]
    if not requirements:
        return '<p class="notice">Requirement structure has not yet been extracted. Consult the official catalog.</p>'
    content = render_level(roots, set(), 0, root=True)
    remaining = [r for r in requirements if r.get('id') not in rendered]
    if remaining:
        content += '<li class="notice">Some recorded groups have unresolved parent relationships. Their recorded rules are shown below; consult the source for their placement.</li>'
        content += render_level(remaining, set(), 0, root=True, parent='unresolved')
    return '<ul class="requirements">' + content + '</ul>'


STATEMENT_TYPES = {
    "learning_outcome": "Learning outcome",
    "program_aim": "Program aim",
    "career_pathway": "Career pathway",
}


def outcomes(p, kind):
    values = [o for o in p.get("outcomes", []) if o.get("kind") == kind]
    sources = {s.get("id"): s for s in p.get("sources", [])}
    if not values:
        return '<p class="muted">Not yet recorded.</p>'
    items = []
    for outcome in values:
        statement_type = STATEMENT_TYPES.get(outcome.get("statement_type"))
        labels = [statement_type] if statement_type else []
        if kind == "inferred_taxonomy":
            labels.append("Documented inference")
        elif not labels:
            labels.append("Source statement")
        label = ' · '.join(labels)
        source = sources.get(outcome.get("source_id"), {})
        items.append(f'<li><span class="badge statement-type">{esc(label)}</span><p class="statement-text">{esc(outcome.get("text"))}</p><small>{external(source.get("url"), "Source")} · {esc(outcome.get("locator") or "Locator not recorded")}</small></li>')
    return '<ul class="outcomes">' + ''.join(items) + '</ul>'


def course_category_markup(course, sources):
    label = esc(CATEGORIES.get(course.get('category'), CATEGORIES['other']))
    review = course.get('category_review') or {}
    if not review:
        return label + '<small class="category-review-status">Legacy / unreviewed classification</small>'
    status = {'reviewed': 'Reviewed classification', 'mixed': 'Mixed subject matter', 'unclassified': 'Insufficient classification evidence'}.get(review.get('status'), 'Unreviewed classification')
    evidence = ' · '.join(external(sources.get(sid, {}).get('url'), 'Classification source') for sid in review.get('source_ids', []))
    candidates = ', '.join(CATEGORIES.get(key, key) for key in review.get('candidate_categories', []))
    return label + '<small class="category-review-status">' + esc(status) + '</small><details class="category-review"><summary>Classification evidence</summary><p>' + esc(review.get('rationale') or 'Rationale not recorded') + '</p>' + ('<p>Candidate subjects: ' + esc(candidates) + '</p>' if candidates else '') + '<p>' + esc(review.get('locator') or 'Locator not recorded') + '</p><p>' + evidence + '</p><small>Taxonomy ' + esc(review.get('taxonomy_version')) + ' · reviewed ' + esc(review.get('reviewed_at')) + '</small></details>'



def course_notes_markup(course):
    notes = [note for note in course.get('notes', []) if isinstance(note, str) and note.strip()]
    if not notes:
        return ''
    label = f"Course notes ({len(notes)})"
    context = course.get('code') or course.get('name') or 'this course'
    items = ''.join(f'<li>{esc(note)}</li>' for note in notes)
    return f'<details class="course-notes"><summary>{label}<span class="sr-only"> for {esc(context)}</span></summary><ul>{items}</ul></details>'


def prerequisite_markup(course, matcher, program_id, base):
    text = course.get('prerequisites')
    if not text:
        return 'Not recorded'
    references = referenced_courses(text, matcher)
    items = []
    for reference in references:
        href = ('#course-' if reference['program_id'] == program_id else base + 'programs/' + reference['program_id'] + '/#course-') + reference['id']
        items.append('<li><a href="' + esc(href) + '">' + esc(reference['code']) + ' · ' + esc(reference['name']) + '</a></li>')
    return '<p class="prerequisite-text">' + esc(text) + '</p>' + ('<span class="prerequisite-title-label">Referenced course titles</span><ul class="prerequisite-titles">' + ''.join(items) + '</ul>' if items else '')


def program_page(p, base, family=None, research=None, institution_programs=()):
    institution = p.get("institution", {})
    courses = unique_courses(p)
    course_sources = {source['id']: source for source in p.get('sources', [])}
    first = p.get("first_offered")
    first_text = "Unknown — not established by the available evidence"
    if first:
        first_text = external(first.get("evidence_url"), first.get("value")) + ' <small>' + esc(first.get("uncertainty") or first.get("precision") or "") + '</small>'
    links = ' <span aria-hidden="true">/</span> '.join(external(link.get("url"), link.get("label") or human(link.get("kind"))) for link in p.get("links", []))
    missing_credits = sum(c.get("credits") is None for c in courses)
    matcher = reference_matcher(p, institution_programs)
    rows = ''.join(f'''<tr><th scope="row" id="course-{esc(c['id'])}">{esc(c.get('code') or 'Unknown')}<span>{esc(c.get('name') or 'Course name not verified')}</span><p class="course-description">{esc(c.get('description') or 'Description not recorded.')}</p>{course_notes_markup(c)}</th><td>{course_category_markup(c, course_sources)}</td><td>{esc(c.get('credits'))}<small>{esc(human(c.get('credit_unit')))}</small></td><td>{prerequisite_markup(c, matcher, p['id'], base)}</td><td>{external(c.get('url'), 'Catalog')}{'<br>' + external(c.get('public_site'), 'Course site') if c.get('public_site') else ''}{'<br>' + external(c.get('syllabus'), 'Syllabus') if c.get('syllabus') else ''}</td></tr>''' for c in courses)
    sources = ''.join(f'''<li id="source-{esc(s.get('id'))}"><h3>{external(s.get('url'), s.get('title') or 'Official source')}</h3><p>{esc(s.get('locator') or 'Locator not recorded')}</p><dl class="source-meta"><div><dt>Retrieved</dt><dd>{esc(s.get('fetched_at') or 'Not recorded')}</dd></div><div><dt>Source date</dt><dd>{esc(s.get('source_date'))}</dd></div><div><dt>Catalog year</dt><dd>{esc(s.get('catalog_year'))}</dd></div><div><dt>Confidence</dt><dd>{esc(human(s.get('confidence')))}</dd></div></dl></li>''' for s in p.get('sources', []))
    notes = ''.join(f'<li>{esc(n)}</li>' for n in p.get('notes', []))
    rankings = institution.get('rankings') or []
    ranking_context = '<section class="cohort-context" aria-label="Institution ranking context"><h2>Cohort context</h2><p>Institution-level U.S. News category membership, not a measure of this program or undergraduate teaching quality. Ranks from different categories are not comparable.</p>'
    if rankings:
        ranking_context += '<ul>'
        for rank in rankings:
            label = f"{rank.get('publisher', 'U.S. News')} {rank.get('edition', 'edition unknown')} · {rank.get('category', 'Category unknown')} · {ranking_label(rank)}"
            ranking_context += f'<li>{external(rank.get("source_url"), label)}<small>Membership evidence: {esc(human(rank.get("verification_status")))}</small></li>'
        ranking_context += '</ul>'
    else:
        ranking_context += '<p>Ranking provenance is not recorded for this institution.</p>'
    ranking_context += '</section>'
    body = f'''<div class="breadcrumb"><a href="{base}">Program index</a><span>/</span>{esc(institution.get('name'))}</div><section class="detail-hero"><div class="eyebrow">{esc(institution.get('name'))} / {esc(p.get('hosting_unit') or 'Hosting unit unknown')}</div><h1>{esc(p.get('title'))}</h1><p class="lede">{esc(p.get('overview') or 'Overview not yet recorded.')}</p><div class="detail-badges">{'' if p.get('program_kind') in {'minor', 'concentration'} else badge('No separate award' if (p.get('major_relationship') or {}).get('kind') == 'second_major_only' else p.get('award_level'))}{badge(human(p.get('program_kind')))}{badge(human(p.get('status')))}</div>{award_options_markup(p)}{major_relationship_markup(p)}{parent_context_markup(p)}<div class="official-links">{links}</div></section>


<nav class="section-nav" aria-label="Program sections"><a href="#outcomes">Program aims &amp; outcomes</a><a href="#requirements">Requirements</a><a href="#curriculum">Curriculum</a><a href="#courses">Course records</a><a href="#sources">Sources</a><a href="#evidence-context">Evidence &amp; review</a></nav>
<section id="outcomes" class="detail-section"><span class="eyebrow">01 / PROGRAM AIMS &amp; OUTCOMES</span><h2>Program aims &amp; outcomes</h2><div class="outcome-grid"><div><h3>Source statements</h3>{outcomes(p, 'source_stated')}</div><div><h3>Inferred taxonomy</h3>{outcomes(p, 'inferred_taxonomy')}</div></div></section>
<section id="requirements" class="detail-section"><span class="eyebrow">02 / PROGRAM STRUCTURE</span><h2>Requirements & choices</h2>{requirement_tree(p, base, matcher)}</section>
<section id="curriculum" class="detail-section"><span class="eyebrow">03 / CURRICULUM PROFILE</span><h2>Required curriculum &amp; elective options</h2>{category_chart(p)}</section>

{family_context(p, family, base)}
<section id="courses" class="detail-section"><span class="eyebrow">04 / COURSE RECORDS</span><h2>Inspect the building blocks</h2><dl class="fact-grid"><div><dt>Calendar</dt><dd>{esc(human(institution.get('calendar')))}</dd></div><div><dt>Catalog year</dt><dd>{esc(p.get('catalog_year'))}</dd></div><div><dt>Last verified</dt><dd>{esc(date_value(p))}</dd></div><div><dt>Requirement inventory</dt><dd>{esc(evidence_label(p))}</dd></div></dl>{metadata_availability(p)}<p class="section-note">Credits retain their original units. “Not recorded” means the atlas lacks evidence; it does not mean a course has no prerequisites.</p><div class="table-scroll" role="region" aria-label="Course records" tabindex="0"><table class="course-table"><thead><tr><th scope="col">Course</th><th scope="col">Category</th><th scope="col">Credits</th><th scope="col">Prerequisites</th><th scope="col">Evidence</th></tr></thead><tbody>{rows}</tbody></table></div>{'<p class="notice">No course records extracted yet.</p>' if not courses else ''}</section>
{ranking_context}{research_program_markup(research, base)}
<section id="sources" class="detail-section"><span class="eyebrow">05 / THE PAPER TRAIL</span><h2>Sources & provenance</h2><ol class="sources">{sources}</ol></section>
<section id="evidence-context" class="detail-section"><h2>Evidence &amp; review status</h2><div class="notice evidence-notice"><strong>Read the evidence in context.</strong><p>Verification: {esc(human(p.get('verification_status')))}. {missing_credits} of {len(courses)} course records have unknown credits. Unknown values are not zero. Recorded course credits must not be added to estimate degree requirements.</p><p class="curriculum-scope">{esc(curriculum_scope(p))}</p><p>First offered: {first_text}</p>{'<ul>' + notes + '</ul>' if notes else ''}</div>{degree_audit_program(p)}</section>'''
    return shell(p.get("title", "Program"), body, base)


def degree_audit_summary(meta):
    audit = meta.get('degree_audit')
    if not audit:
        return ''
    stats = [('audited', 'First-pass audited'), ('blocked', 'Blocked / incomplete review'), ('in_progress', 'In progress'), ('pending', 'Pending'), ('second_pass_verified', 'Independent second pass verified')]
    counts = ''.join('<div><dt>' + label + '</dt><dd>' + esc(audit.get(key, 0)) + '</dd></div>' for key, label in stats)
    return '<section class="degree-audit-summary notice" aria-labelledby="degree-audit-title"><h2 id="degree-audit-title">Degree correctness audit</h2><p>' + esc(audit.get('scope_programs')) + ' standalone degree records in scope · ' + esc(audit.get('audit_date') or 'Date not recorded') + '.</p><dl class="metadata-counts">' + counts + '</dl><p>These counts describe whole-degree reviews, including applicable policies. Earlier “complete requirement inventory” labels do not certify this separate correctness review. Blocked reviews retain verified corrections and explicit evidence gaps; counts do not imply that the remaining programs are correct or incorrect.</p><p>Degree pages separately report bounded independent reviews of fixed requirements, choice rules and chart classification, with their own evidence and limitations. A verified dimension does not certify the whole degree; an unresolved policy does not erase a verified curriculum correction. Missing dimensions are labeled “Not independently reviewed”; an explicit unverified judgment is labeled “Not verified from available evidence.”</p></section>'


def degree_audit_program(program):
    if program.get('program_kind') == 'additional_major':
        return additional_major_audit_program(program)
    if program.get('program_kind') != 'degree':
        return ''
    audit = program.get('degree_audit')
    state = human(audit.get('status')) if audit else 'Pending'
    second = human(audit.get('second_pass_status') or 'pending') if audit else 'Pending'
    core = (audit or {}).get('core_review') or {}
    return '<section class="notice degree-audit-program" aria-labelledby="program-audit-title"><h2 id="program-audit-title">Whole-degree correctness audit: ' + esc(state) + '</h2><p>Whole-degree independent second pass: ' + esc(second) + '. These statuses include applicable degree policies and are separate from requirement inventory and course metadata coverage.</p><h3>Bounded independent review</h3><p>Each judgment applies only to its stated source scope. Unresolved policies can coexist with verified fixed courses, choice rules or chart classifications.</p>' + review_dimensions(core) + '</section>'


def additional_major_audit_program(program):
    review = program.get('additional_major_audit')
    if not review:
        return ''
    display = {**review, 'dimensions': {**review['dimensions'], 'eligibility': review['eligibility_review']}}
    return '<section class="notice additional-major-audit-program" aria-labelledby="program-audit-title"><h2 id="program-audit-title">Additional-major correctness review</h2><p>This review covers the additional major and its eligibility rules. It does not certify the complete host degree.</p><p>' + esc(review['scope_summary']) + '</p>' + review_dimensions(display, additional=True) + '</section>'


def review_dimensions(core, additional=False):
    dimensions = core.get('dimensions') or {}
    rows = []
    labels = [('fixed_requirements', 'Fixed requirements'), ('choice_rules', 'Choice rules'), ('classification', 'Chart classification')]
    if additional:
        labels.append(('eligibility', 'Second-major eligibility'))
    for key, label in labels:
        dimension = dimensions.get(key) or {}
        status = {'verified': 'Verified within stated scope', 'partial': 'Partially reviewed', 'unverified': 'Not verified from available evidence'}.get(dimension.get('status'), 'Not independently reviewed')
        summary = '<p>' + esc(dimension['summary']) + '</p>' if dimension.get('summary') else ''
        evidence = ''.join('<li>' + external(item.get('url'), item.get('locator') or 'Review source') + '</li>' for item in dimension.get('evidence', []))
        limitations = ''.join('<li>' + esc(item) + '</li>' for item in dimension.get('limitations', []))
        details = ''
        if evidence or limitations:
            details = '<details><summary>Evidence &amp; limitations</summary>'
            details += '<h4>Evidence</h4><ul>' + evidence + '</ul>' if evidence else '<p>No evidence links recorded.</p>'
            details += '<h4>Scope limitations</h4><ul>' + limitations + '</ul>' if limitations else ''
            details += '</details>'
        rows.append('<div class="review-dimension" data-review-dimension="' + key + '"><dt>' + label + '</dt><dd><strong class="review-dimension-status">' + status + '</strong>' + summary + details + '</dd></div>')
    provenance = ''
    if core:
        provenance = '<p class="review-provenance">Reviewed: ' + esc(core.get('reviewed_at') or 'Date not recorded') + ' · Reviewer: ' + esc(core.get('reviewer') or 'Not recorded') + '.</p>'
    return provenance + '<dl class="review-dimensions">' + ''.join(rows) + '</dl>'


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
        return '<br>'.join(external(r.get('source_url'), f"{r.get('category', 'Category unknown')} · {ranking_label(r)} ({r.get('edition', '?')})") + '<small>' + esc(human(r.get('verification_status'))) + '</small>' for r in i.get('rankings', [])) or 'Not recorded'

    rows = ''.join(f'<tr><th scope="row">{external(i.get("website"), i.get("name"))}</th><td>{ranking_evidence(i)}</td><td>{badge(human(i.get("coverage_status") or "pending"))}</td><td>{esc(i.get("coverage_note") or "Inspection evidence not yet recorded.")}{coverage_evidence(i)}</td><td>{len(i.get("program_ids") or [])}</td></tr>' for i in sorted(institutions, key=lambda i: i.get('name', '')))
    cohort = meta.get('cohort') if isinstance(meta.get('cohort'), dict) else {}
    cohort_notes = ''.join(f'<li><strong>{esc(c.get("category"))}:</strong> {esc(c.get("note"))}</li>' for c in cohort.get('category_coverage', []))
    summary = meta.get('coverage_summary')
    summary = summary if isinstance(summary, str) else 'This atlas is a documented pilot. The listed institutions are not a complete ranking cohort.'
    body = f'''<section class="page-hero"><span class="eyebrow">THE BOUNDARIES OF THE EVIDENCE</span><h1>Coverage &amp; limitations</h1><p class="lede">An absent record is not an absent program. This ledger makes the state of the research visible.</p></section><div class="notice"><strong>{esc(summary)}</strong><ul>{limitations(meta)}</ul></div>
{degree_audit_summary(meta)}<section class="detail-section"><h2>Recorded institutions</h2><p class="section-note">{len(institutions)} institution records · {len(data.get('programs', []))} documented programs. These are inventory counts, not a percentage of the intended cohort. {identity_only} records are identity-only with curriculum extraction pending; {len(data.get("programs", [])) - identity_only} have curriculum extraction in progress or complete. Counts include all documented records. Discovery links can identify additional programs awaiting a record.</p>{'<ul class="section-note">' + cohort_notes + '</ul>' if cohort_notes else ''}<div class="status-grid">{''.join('<div><strong>' + str(v) + '</strong><span>' + esc(human(k)) + '</span></div>' for k, v in sorted(statuses.items()))}</div><div class="table-scroll" role="region" aria-label="Institution coverage" tabindex="0"><table class="coverage-table"><thead><tr><th>Institution</th><th>Cohort membership</th><th>Research status</th><th>Evidence / remaining work</th><th>Documented records</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="detail-section prose"><h2>How to read a status</h2><dl class="definitions"><dt>Confirmed</dt><dd>An official source identifies a qualifying program. Curriculum extraction may still be partial.</dd><dt>No qualifying program found</dt><dd>A documented inspection of official catalogs and program directories found no qualifying title. This is a bounded search result, not proof of absence.</dd><dt>Inspected</dt><dd>Research has begun or sources have been inspected; use the evidence note for the precise conclusion.</dd><dt>Inaccessible</dt><dd>Required evidence could not be accessed. No conclusion about program existence follows.</dd><dt>Pending</dt><dd>Not yet inspected or no sufficient evidence recorded.</dd></dl><h2>The intended scope</h2><p>Two independent U.S. News cohorts: National Universities and National Liberal Arts Colleges ranked 100 or better, including ties. The latest edition and complete membership require source verification; a verified edition does not establish a complete institution roster. Program inclusion requires AI or Artificial Intelligence in the official undergraduate title.</p><p>Research generation: {esc(meta.get('generated_at') or 'Not recorded')}.</p><a href="{base}methodology/">Read the full methodology →</a></section>'''
    return shell('Coverage & limitations', body, base, 'coverage')


def research_program_markup(context, base):
    if context is None:
        return ''
    rows=''.join('<tr data-research-field="'+esc(row['field'])+'"><th scope="row">'+esc(row['label'])+'</th><td>'+esc(row['score_text'])+'</td><td>'+esc(row['rank_text'])+'</td><td>'+esc(row['adjusted_count_text'])+'</td><td>'+esc(row['status_label'])+'</td></tr>' for row in context['rows'])
    upstream='<p class="section-note">Matched upstream institution: '+esc(context['upstream_institution'])+'.</p>' if context.get('upstream_institution') else ''
    return '<section id="research-context" class="detail-section research-context" aria-labelledby="research-context-title"><span class="eyebrow">INSTITUTION RESEARCH CONTEXT</span><h2 id="research-context-title">CSRankings publication activity</h2><p class="section-note">'+esc(context.get('year_start'))+'–'+esc(context.get('year_end'))+' · United States · institution-level research. These values do not measure undergraduate teaching or the quality of this program. Programs at the same institution share this context.</p>'+upstream+'<div class="table-scroll" role="region" aria-label="CSRankings research fields" tabindex="0"><table class="research-table"><caption>Five research fields and their aggregate; ranks use the full U.S. population for each selection.</caption><thead><tr><th scope="col">Research selection</th><th scope="col">Displayed score</th><th scope="col">U.S. research rank</th><th scope="col">Adjusted publications</th><th scope="col">Source status</th></tr></thead><tbody>'+rows+'</tbody></table></div><p class="section-note">Individual field scores are adjusted publication counts + 1. The aggregate is the geometric mean of the five field scores; it is not an average of ranks. Displayed scores use one decimal and ties share competition ranks. Adjusted counts here use three decimals for readability; full precision remains in the public data. Missing observations stay unavailable, without a zero score or last-place rank.</p><p><a href="'+base+'methodology/#research">Research methodology, source snapshot &amp; reuse scope →</a></p></section>'


def research_method_markup(cs):
    method=cs.get('methodology') or {}
    if not isinstance(method,dict):
        text=method if isinstance(method,str) else 'CSRankings is a publication-based view of computer science research activity.'
        return badge('CSRankings · not imported')+'<p>'+esc(text)+'</p><p>No research values are available in this snapshot. Missing values do not mean zero publications or no AI research.</p><p>'+external('https://csrankings.org/','Visit CSRankings')+' · '+external('https://csrankings.org/faq','Read the CSRankings FAQ')+'</p>'
    available=method.get('status')=='available'
    fields=', '.join(RESEARCH_FIELDS.get(field,field) for field in method.get('fields',[])) or 'Not configured'
    missingness=sorted({o.get('missingness') for o in cs.get('observations',[]) if o.get('missingness')})
    settings=[('Publication years',str(method.get('year_start','Unknown'))+'–'+str(method.get('year_end','Unknown'))),('Country','United States' if method.get('geographic_filter') == 'us' else method.get('geographic_filter') or 'Not recorded'),('Research fields',fields)]
    config='<dl class="research-config">'+''.join('<div><dt>'+esc(label)+'</dt><dd>'+esc(value)+'</dd></div>' for label,value in settings)+'</dl>'
    if not available:
        source_details = '<details class="research-provenance"><summary>Saved source details</summary><p>Source version: ' + esc(method.get('source_snapshot') or 'Not recorded') + '</p><p>' + esc(method.get('method') or 'Calculation note not recorded') + '</p><p>Recorded data-status labels: ' + esc(', '.join(missingness) or 'Not recorded') + '</p></details>'
        return badge('CSRankings · not imported')+'<p>No research scores are available in this saved view. Missing figures do not mean zero publications or a last-place rank. Data that still require permission remain unavailable.</p>'+config+'<p>'+external(method.get('source_url') or 'https://csrankings.org/faq','Research source')+'</p>'+source_details
    snapshot=str(method.get('source_snapshot') or '')
    copying='https://github.com/emeryberger/CSrankings/blob/'+snapshot+'/COPYING' if re.fullmatch('[0-9a-f]{40}',snapshot) else 'https://github.com/emeryberger/CSrankings/blob/gh-pages/COPYING'
    population=cs.get('population') or {}
    population_rows=[]
    if population.get('listed_us_institutions') is not None:
        population_rows.append(('Listed U.S. institutions',population['listed_us_institutions']))
    if (population.get('ranked_institutions_by_field') or {}).get('aggregate') is not None:
        population_rows.append(('U.S. institutions with selected output across the five fields',population['ranked_institutions_by_field']['aggregate']))
    config+='<dl class="research-config">'+''.join('<div><dt>'+esc(label)+'</dt><dd>'+esc(value)+'</dd></div>' for label,value in population_rows)+'</dl>' if population_rows else ''
    permission=method.get('permission') or {}
    venue_rows=''.join('<div><dt>'+esc(RESEARCH_FIELDS.get(field,field))+'</dt><dd>'+esc(', '.join(venues))+'</dd></div>' for field,venues in (method.get('field_membership') or {}).items())
    sources=''.join('<li>'+external(source.get('url'),source.get('filename') or 'Source file')+('<br><code>SHA-256: '+esc(source['sha256'])+'</code>' if source.get('sha256') else '')+'</li>' for source in method.get('sources',[]) if isinstance(source,dict))
    details='<details class="research-provenance"><summary>Sources, publication venues and reuse permission</summary><h3>Saved source version</h3><p>' + esc(snapshot or 'Not recorded') + '</p>' + ('<p>Original calculation note: ' + esc(method.get('method')) + '</p>' if method.get('method') else '') + ('<p>Recorded data-status labels: ' + esc(', '.join(missingness)) + '</p>' if missingness else '')
    if venue_rows:details+='<h3>Selected venue groups</h3><dl class="research-config">'+venue_rows+'</dl><p>The separate KDD conference option is not included. Robotics is outside the five selected fields.</p>'
    if permission:details+='<h3>Project permission record</h3><p>'+esc(permission.get('statement') or 'Educational-project permission confirmed by the project owner.')+'</p><p>Confirmed: '+esc(permission.get('confirmed_date'))+' · Scope: '+esc(permission.get('scope'))+'. No broader permission is inferred.</p>'
    if method.get('retrieved_date'):details+='<p>Source retrieved: '+esc(method['retrieved_date'])+'.</p>'
    if sources:details+='<h3>Snapshot sources</h3><ul>'+sources+'</ul>'
    details+='</details>'
    attribution=method.get('attribution') or {}
    attribution_text='CSRankings' + (' by '+str(attribution['maintainer']) if attribution.get('maintainer') else '')
    snapshot_link=external('https://github.com/emeryberger/CSrankings/tree/'+snapshot,'Pinned source snapshot') if re.fullmatch('[0-9a-f]{40}',snapshot) else ''
    attribution_note='<p>'+esc(attribution['publication_data'])+'</p>' if attribution.get('publication_data') else ''
    notes=''.join('<p>'+esc(method[key])+'</p>' for key in ('license_explanation','license_notes','missingness_explanation') if method.get(key))
    details = details.replace('</details>', '<h3>Source notices</h3>' + attribution_note + notes + '</details>')
    return badge('CSRankings · research context available')+'<p>The homepage’s AI Ranking describes university research publications in five areas of computer science. It comes from CSRankings. It does not measure undergraduate teaching, curriculum depth, admissions outcomes or the quality of an individual program.</p>'+config+'<h3>How the scores and ranks are calculated</h3><p>Publications are counted using the authors, university affiliations and conferences recorded in the saved CSRankings source. A paper can give a fraction of its credit to an author. The counts are not divided by faculty size, and they do not reconstruct past faculty affiliations or student enrollment.</p><p>Each field’s score is its credited publication count plus one. The overall five-field score is the geometric mean: multiply the five field scores, then take the fifth root. We do not subtract one afterward. This combines scores, not an average of ranks.</p><p>Scores are rounded to one decimal before ranks are assigned. Equal rounded scores share a rank, and the next rank skips the places occupied by the tie. Ranks use the full eligible U.S. group with publications in the selected field or fields, before matching universities to this Atlas. They are not rankings of just the institutions shown here.</p><p>The publication years above are completed calendar years. The live CSRankings website also includes the current year by default, so its default results can differ from this project’s saved view. Every program at the same university shares that university’s research figures.</p><h3>When research information is missing</h3><p>A missing number does not mean zero publications, no AI research or a last-place rank. We distinguish universities with no publications in the selected venues from universities that CSRankings does not list, universities outside the eligible U.S. group, names that have not been matched, and unavailable source data.</p><h3>Sources and permission</h3><p>Project owner Kris Jordan confirmed permission for this educational project on October 11, 2026. This does not claim broader reuse rights or replace the source’s license notices.</p><p>'+external('https://csrankings.org/',attribution_text)+' · '+external('https://csrankings.org/faq','How CSRankings works')+' · '+external(copying,'COPYING and license notices')+' · '+external(method.get('source_url'),'Source website')+(' · '+snapshot_link if snapshot_link else '')+'</p>'+details



def methodology_page(data, base):
    meta = data.get('meta', {})
    research_markup = research_method_markup(data.get('csrankings') or {})
    body = f'''<section class="page-hero"><span class="eyebrow">HOW TO READ THE ATLAS</span><h1>Sources &amp; methodology</h1><p class="lede">What we include, where the information comes from, and how to read the comparisons. Course counts and research rankings describe different things; neither is a score for program quality.</p></section>
<div class="method-layout"><nav class="method-nav" aria-label="Methodology sections"><a href="#scope">01 · What we include</a><a href="#evidence">02 · Our sources</a><a href="#curriculum-method">03 · Course comparisons</a><a href="#research">04 · Research rankings</a><a href="#unknowns">05 · Limits</a></nav><div class="prose">
<section id="scope"><h2>01 / What we include</h2><p>A program is included when its official undergraduate title contains AI or Artificial Intelligence. Terms such as GenAI and GeoAI count when the university explicitly identifies them as artificial intelligence. Unrelated words containing those letters do not count. A general computer science degree is not included simply because it offers AI electives.</p><p>Degrees, additional majors (including second majors), minors, and concentrations are listed separately. A minor or concentration describes that particular course of study, not an entire bachelor’s degree.</p><p>The project aims to cover two separate U.S. News groups: National Universities and National Liberal Arts Colleges ranked 100 or better, including ties. The full institution list has not yet been verified. The <a href="{base}coverage/">coverage page</a> shows which institutions and programs have been checked and what remains unfinished. U.S. News ranks provide institution context; ranks from these two groups should not be compared directly.</p></section>
<section id="evidence"><h2>02 / Where the information comes from</h2><p>Program information comes from official university catalogs, program pages and announcements. Source links let you inspect the original evidence. We record the catalog year when available, the date a source was consulted, the section used and our confidence in that source.</p><p>A verification date tells you when the Atlas record was checked. The university may change its information afterward. We record a program’s start date only when a source supports it; the oldest search result is not evidence of the first year a program was offered.</p><p>Statements about learning outcomes, program aims and career pathways are distinguished when the source provides that information. They are separate from inferred themes: interpretations made by the Atlas rather than claims made by the university.</p><p>Reviews can cover different things. Checking a list of required courses does not necessarily establish every elective rule, graduation policy or course classification. Read the scope and remaining limitations beside each review.</p></section>
{degree_audit_summary(meta)}
<section id="curriculum-method"><h2>03 / How to read the course comparisons</h2><h3>Required courses and options are different counts</h3><p>Required curriculum counts individually required courses plus simple required selections that can be counted safely. For example, “choose two of six courses” contributes two required courses, not six. A selection is included only when its full list is represented, its courses have the same known subject category, and they do not overlap another counted requirement.</p><p>Selections based on credits, choices within choices, mixed subjects and unresolved overlaps are kept with their individual rules. We do not choose a sample pathway, add overlapping choices together or assume that every listed course must be taken. These counts do not describe the whole degree.</p><p>Elective options counts the different courses a student might choose, including options that satisfy required choices. Courses already counted as individually required are excluded from this view. A large option list does not mean a student must take more electives.</p><p>Each view counts a course identity once. Cross-listed courses are combined only when official evidence confirms that they are the same course. Similar names or ordinary substitutions are not enough. Courses recorded only as background or with an unclear place in the requirements are not treated as compulsory.</p><h3>What the subject labels mean</h3><p>We use course descriptions, stated aims or syllabi to identify the main subject. AI in a title is insufficient: AI &amp; machine learning requires evidence that students learn AI methods, such as how models are built or trained, or how search and reasoning methods work. Learning to use AI tools in a discipline belongs in Domain studies &amp; applications when that is the main aim. Courses mainly about ethics or society belong in Human context.</p><p>Mathematics and Statistics currently share one category. A finer split has not been reviewed. Computing foundations covers programming and basic computer-science methods; Systems covers computing infrastructure. Other / unclassified includes mixed subjects and courses without enough evidence for a clear category. Electives is an older label; newly reviewed courses are classified by subject.</p><p>Reviewed classifications have a source and an explanation. Legacy or unreviewed labels have not passed that course-review standard. These labels do not measure teaching quality or how deeply a topic is taught. “0 mapped” means no courses have been assigned to that subject in the selected view. It does not establish that the actual curriculum lacks the subject.</p><h3>What “complete” and the credit figures mean</h3><p>Complete means that the requirements for the stated program and catalog year have been reviewed. It does not guarantee that every course description or prerequisite is available. A complete minor or concentration does not certify the requirements of its parent degree. Course-subject reviews and requirement completeness are separate judgments.</p><p>Credits retain the university’s units: semester hours, quarter hours, course units or other units. We do not convert them or add recorded course credits to estimate a degree total. An unknown amount is missing information, not zero. A missing prerequisite statement does not mean that a course has no prerequisites.</p><h3>Related programs still have separate requirements</h3><p>Related degrees are grouped only when a sourced relationship has been recorded; a similar title is not enough. Each degree keeps its own page, award and requirements. Labels show which requirements are shared, local to a variant or replacements. “Local” does not mean a requirement is necessarily unique to that program.</p><p>A collapsed university row can show a range of course counts across its matching programs. That range is not a combined curriculum. Comparisons use each program’s requirements after its stated exclusions and replacements. The discipline filter uses only recorded relationships.</p></section>
<section id="research"><h2>04 / What the research ranking tells you</h2>{research_markup}</section>
<section id="unknowns"><h2>05 / What remains uncertain</h2><p>Coverage is incomplete. A missing program or institution does not establish that it does not exist. “No qualifying program found” means a documented search of official sources found none within its stated scope; it is not a claim about every possible program or future offering.</p><p>Some sources cannot be accessed, and some research has not yet been completed. Those limits remain visible. The following notes describe the current boundaries of the project:</p><ul>{limitations(meta)}</ul><p>Use the Atlas to compare documented information and frame questions. Confirm current admission and graduation requirements with the university.</p><a href="{base}coverage/">See coverage and remaining work →</a></section></div></div>'''
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
    for asset in ('atlas.css', 'atlas.js', 'requirements.js'):
        shutil.copyfile(Path(__file__).parent / 'web' / asset, output / 'assets' / asset)
    from .static_api import build_api, documentation_body
    build_api(data, output, base)
    pages = {'api/index.html': shell('JSON API', documentation_body(data, base), base, 'api'), 'index.html': root_page(data, base), 'coverage/index.html': coverage_page(data, base), 'methodology/index.html': methodology_page(data, base)}
    family_map = {f['id']: dict(f) for f in data.get('families', [])}
    for family in family_map.values():
        family['_variant_labels'] = [(p['id'], (p.get('family') or {}).get('variant_label') or p.get('title')) for p in programs if p['id'] in family.get('variant_ids', [])]
    institution_programs = {}
    for program in programs:
        institution_id = (program.get('institution') or {}).get('id')
        if institution_id:
            institution_programs.setdefault(institution_id, []).append(program)
    for program in programs:
        pages[f'programs/{program["id"]}/index.html'] = program_page(program, base, family_map.get((program.get('family') or {}).get('id')), institution_context(data, (program.get('institution') or {}).get('id')), institution_programs.get((program.get('institution') or {}).get('id'), []))
    for relative, content in pages.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    (output / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / '.nojekyll').touch()
