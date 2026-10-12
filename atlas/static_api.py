"""Versioned read-only files derived exclusively from the curated public export."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from .curriculum_profile import requirement_profile

VERSION = '1.0.1'
SLUG = r'[a-z0-9]+(?:-[a-z0-9]+)*'


def encode(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def schemas() -> dict:
    """Load the checked-in contract; never infer a contract from a build's data."""
    return json.loads(Path(__file__).with_name('api_schema.json').read_text())['$defs']


def ref(name: str) -> dict:
    return {'$ref': f'#/components/schemas/{name}'}


def array(name: str) -> dict:
    return {'type': 'array', 'items': ref(name)}


def program_index(program: dict, base: str) -> dict:
    pid = program['id']
    return {
        'id': pid, 'title': program['title'],
        'institution_id': program['institution']['id'],
        'program_kind': program.get('program_kind'), 'award_level': program.get('award_level'),
        'curriculum_status': program.get('curriculum_status'),
        'verification_status': program.get('verification_status'),
        'family_id': (program.get('family') or {}).get('id'),
        'detail_url': f'{base}api/v1/programs/{pid}.json',
        'page_url': f'{base}programs/{pid}/',
    }


def responses(data: dict, base: str) -> dict:
    """All response bodies, with canonical program-local course/requirement IDs."""
    bodies = {
        'dataset.json': data,
        'metadata.json': data.get('meta', {}),
        'programs.json': [program_index(p, base) for p in data.get('programs', [])],
        'institutions.json': data.get('institutions', []),
        'families.json': data.get('families', []),
        'rankings.json': {'rankings': data.get('rankings', []),
                          'csrankings': data.get('csrankings', {})},
    }
    for collection in ('programs', 'institutions', 'families'):
        seen = set()
        for record in data.get(collection, []):
            rid = record['id']
            if not re.fullmatch(SLUG, rid) or rid in seen:
                raise ValueError(f'Invalid or duplicate API {collection} ID: {rid}')
            seen.add(rid)
            bodies[f'{collection}/{rid}.json'] = record
            if collection == 'programs':
                bodies[f'courses/{rid}.json'] = record.get('courses', [])
                bodies[f'requirements/{rid}.json'] = record.get('requirements', [])
                bodies[f'profiles/{rid}.json'] = requirement_profile(
                    record, include_course_ids=True)
    return bodies


def openapi(data: dict, base: str) -> dict:
    components = json.loads(json.dumps(schemas()).replace('#/$defs/', '#/components/schemas/'))
    nullable_string = {'type': ['string', 'null']}
    components['ProgramIndexEntry'] = {
        'type': 'object', 'additionalProperties': False,
        'required': list(program_index({'id': 'example', 'title': 'Example',
                                       'institution': {'id': 'example'}}, base)),
        'properties': {key: {'type': 'string'} for key in (
            'id', 'title', 'institution_id', 'detail_url', 'page_url')}
        | {key: nullable_string for key in ('program_kind', 'award_level',
            'curriculum_status', 'verification_status', 'family_id')},
    }
    components['Manifest'] = {
        'type': 'object', 'required': ['api_version', 'dataset_sha256', 'counts', 'endpoints'],
        'properties': {
            'api_version': {'type': 'string', 'const': VERSION},
            'dataset_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
            'counts': {'type': 'object', 'additionalProperties': {'type': 'integer', 'minimum': 0}},
            'endpoints': {'type': 'object', 'additionalProperties': {'type': 'string'}},
        }, 'additionalProperties': False,
    }
    paths = {}

    def add(path, schema, summary, example=None, parameter=None):
        operation = {
            'summary': summary,
            'responses': {
                '200': {'description': 'Generated public JSON file.', 'content': {
                    'application/json': {'schema': schema, **(
                        {'examples': {'current': {'externalValue': example}}} if example else {})}}},
                '404': {'description': 'File not found. GitHub Pages returns an HTML error page; '
                        'there is no JSON error envelope or runtime fallback.',
                        'content': {'text/html': {'schema': {'type': 'string'}}}},
            },
        }
        if parameter:
            operation['parameters'] = [{'name': parameter, 'in': 'path', 'required': True,
                'description': 'Use an ID from the corresponding index. Course and requirement '
                               'files use a program ID, not a global course ID.',
                'schema': {'type': 'string', 'pattern': '^' + SLUG + '$'}}]
        paths[path] = {'get': operation}

    for filename, name, summary in (
        ('index.json', 'Manifest', 'API version, content digest, counts and download paths'),
        ('dataset.json', 'Dataset', 'Complete canonical public curated dataset'),
        ('metadata.json', 'Metadata', 'Coverage, limitations and review summaries'),
        ('programs.json', None, 'Concrete program index with stable IDs and detail links'),
        ('institutions.json', None, 'Institution index including coverage and program IDs'),
        ('families.json', None, 'Reviewed program families and variant IDs'),
        ('rankings.json', 'Rankings', 'Institution rankings and pinned CSRankings results'),
    ):
        shape = ref(name) if name else array({'programs.json': 'ProgramIndexEntry',
            'institutions.json': 'Institution', 'families.json': 'Family'}[filename])
        add('/' + filename, shape, summary, base + 'api/v1/' + filename)
    for collection, name, parameter in (
        ('programs', 'Program', 'program_id'), ('institutions', 'Institution', 'institution_id'),
        ('families', 'Family', 'family_id'), ('courses', 'Course', 'program_id'),
        ('requirements', 'Requirement', 'program_id'), ('profiles', 'Profile', 'program_id'),
    ):
        records = data.get(collection if collection in ('institutions', 'families') else 'programs', [])
        example = base + f'api/v1/{collection}/{records[0]["id"]}.json' if records else None
        add(f'/{collection}/{{{parameter}}}.json', array(name) if collection in (
            'courses', 'requirements') else ref(name), f'{name} data for one stable ID',
            example, parameter)
    return {
        'openapi': '3.1.0', 'jsonSchemaDialect': 'https://json-schema.org/draft/2020-12/schema',
        'info': {'title': 'AI Program Atlas static JSON API', 'version': VERSION,
            'description': 'Build-generated read-only files. No query filtering, pagination, '
                'authentication or server runtime. Unknown facts remain null; omitted optional '
                'fields are not evidence of absence. Credits retain recorded units. '
                'The dataset date is the latest evidence date, not a build timestamp. '
                'v1 is a contract major version, not an immutable dataset snapshot.'},
        'servers': [{'url': base + 'api/v1'}], 'paths': paths,
        'components': {'schemas': components},
    }


def build_api(data: dict, output: Path, base: str) -> None:
    bodies = responses(data, base)
    bodies['index.json'] = {
        'api_version': VERSION,
        'dataset_sha256': hashlib.sha256(encode(data).encode()).hexdigest(),
        'counts': {key: len(data.get(key, [])) for key in ('programs', 'institutions', 'families')},
        'endpoints': {key: base + 'api/v1/' + key for key in (
            'dataset.json', 'programs.json', 'institutions.json', 'families.json',
            'rankings.json', 'metadata.json', 'openapi.json', 'schema.json')},
    }
    contract = openapi(data, base)
    bodies['openapi.json'] = contract
    bodies['schema.json'] = {'$schema': contract['jsonSchemaDialect'],
        '$ref': '#/components/schemas/Dataset', 'components': contract['components']}
    root = output / 'api' / 'v1'
    # This subtree belongs exclusively to this generator: remove obsolete ID files on rebuild.
    if root.exists():
        shutil.rmtree(root)
    for relative, value in bodies.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encode(value), encoding='utf-8')


def documentation_body(data: dict, base: str) -> str:
    """Static accessible documentation; all interpolated identifiers are validated slugs."""
    from html import escape

    api = base + 'api/v1/'
    programs = data.get('programs', [])
    pid = programs[0]['id'] if programs else None
    example_url = api + f'programs/{pid}.json' if pid else api + 'programs.json'
    rows = ''.join(f'<tr><th scope="row"><a href="{api}{path}" download>{path}</a></th>'
                   f'<td>{description}</td></tr>' for path, description in (
        ('dataset.json', ('Complete public dataset: all programs, institutions, families, '
         'requirements, courses, reviews, sources and ranking snapshots.')),
        ('index.json', 'API version, SHA-256 dataset digest, counts and download links.'),
        ('programs.json', 'Program IDs, identity, review status and detail links.'),
        ('institutions.json', 'Institutions, coverage, rankings and program IDs.'),
        ('families.json', 'Reviewed shared rules, sources and concrete variant IDs.'),
        ('rankings.json', ('U.S. News evidence and CSRankings methodology, observations, '
         'full U.S. results and population.')),
        ('metadata.json', 'Coverage, evidence date, audit summaries and limitations.'),
    ))
    example = escape("const response = await fetch('" + example_url + "');\n"
                     "if (!response.ok) throw new Error(`HTTP ${response.status}`);\n"
                     "const program = await response.json();\nconsole.log(program);")
    detail_links = ''
    if pid:
        detail_links = '<p>Working examples: ' + ' · '.join(
            f'<a href="{api}{collection}/{pid}.json">{label}</a>' for collection, label in (
                ('programs', 'Program'), ('courses', 'Courses'),
                ('requirements', 'Requirements'), ('profiles', 'Curriculum profile'))) + '.</p>'
    return f'''<section class="page-hero"><span class="eyebrow">PUBLIC DATA / API v1</span>
<h1>Static JSON API</h1><p class="lede">Download the source-backed Atlas data for research,
analysis and your own tools. Each response is a file generated with this site.</p>
<p><a href="{api}dataset.json" download>Download complete dataset →</a> ·
<a href="{api}openapi.json" download>OpenAPI 3.1 contract</a> ·
<a href="{api}schema.json" download>JSON Schema</a></p></section>
<div class="prose api-docs"><section aria-labelledby="api-downloads"><h2 id="api-downloads">Downloads</h2>
<div class="table-scroll"><table><caption>Files beneath <code>{api}</code></caption>
<thead><tr><th scope="col">File</th><th scope="col">Contents</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>The complete export is the canonical public dataset. The existing <a href="{base}data.json">data.json</a>
URL remains a compatibility copy with identical bytes. Detail files are projections of that same export.</p></section>
<section aria-labelledby="api-details"><h2 id="api-details">Stable detail paths</h2>
<p>Read an index to discover IDs, then download <code>programs/{{program_id}}.json</code>,
<code>institutions/{{institution_id}}.json</code> or <code>families/{{family_id}}.json</code>.
For each program, <code>courses/{{program_id}}.json</code> and
<code>requirements/{{program_id}}.json</code> return its full arrays.
<code>profiles/{{program_id}}.json</code> returns the centrally derived course partitions,
choice descriptors and conservative required-obligation counts used by the site.</p>
{detail_links}<p>Course, source and requirement IDs are local to their program (or family),
so retain the owning ID when joining records. Requirement <code>parent_id</code> preserves
nested rules; <code>course_ids</code> references that program’s courses. Family variants retain
concrete awards, resolved requirements, origins, replacements and evidence. Program requirements
already contain inherited rules; do not add family rules again.</p></section>
<section aria-labelledby="api-example"><h2 id="api-example">Fetch a file</h2>
<pre class="api-code"><code>{example}</code></pre>
<p>These are read-only GET downloads, with no authentication, filtering, pagination or search
service. Query parameters do not select data. Download an index or the dataset and filter locally.
An unknown ID returns the host’s HTML 404 page, not a JSON error object. Check the HTTP status
before parsing. Examples use this site’s configured base path; same-origin browser fetches work.
Cross-origin availability depends on the hosting service’s headers.</p></section>
<section aria-labelledby="api-meaning"><h2 id="api-meaning">Scope, unknowns and units</h2>
<p>Coverage and curriculum review remain incomplete. An unlisted program does not establish
absence, and a partial curriculum does not establish every requirement. Review statuses,
source citations, uncertainty notes and limitations travel with the records. Raw source captures,
private notes, refresh logs, database history and credentials are excluded.</p>
<p><code>null</code> means unknown or unavailable; it is never silently changed to zero.
An omitted optional field means no recorded value, not evidence of absence. Empty course or
requirement arrays mean no represented records, not that a credential has no curriculum.
Use explicit coverage and ranking missingness labels to interpret missing data.</p>
<p>Credits retain <code>credit_unit</code>: semester hours, quarter hours, units, course units
or unknown. No conversions or degree totals are inferred. Profile counts are distinct documented
course identities. Option-pool size is not elective workload; nested, conditional, overlapping
and credit-based choices retain their source rules and conservative counting exclusions.</p>
<p>CSRankings values are publication-research scores, with fractional counts and competition
ranks where recorded. The methodology preserves the window, fields, venues, attribution,
permission statement and pinned snapshot. U.S. News ranks keep their edition and category.
Neither describes undergraduate teaching quality. See <a href="{base}methodology/">sources
and methodology</a> and the source notices before reuse; access does not grant new redistribution
rights to upstream catalogs or ranking material.</p></section>
<section aria-labelledby="api-version"><h2 id="api-version">Versioning and reproducibility</h2>
<p>The contract version is {VERSION}. Breaking structural changes require a new major path.
Within v1, additive fields and new records may appear; accept optional additions. The data change
with curated releases, so v1 is not an immutable archive. Retain a downloaded dataset and its
<code>dataset_sha256</code> from the manifest to identify an exact snapshot.</p>
<p><code>meta.generated_at</code> is the latest recorded evidence date, not the time the files
were built or a guarantee that every source was checked that day. Identical public data and base
paths produce byte-identical files. Build locally with <code>uv run atlas build --base-path
/ai-program-atlas/</code>. The <a href="{api}openapi.json">OpenAPI contract</a> provides reusable
typed schemas and links to actual response examples.</p></section></div>'''
