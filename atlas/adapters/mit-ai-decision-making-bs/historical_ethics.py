"""Explicit two-payload observation for one historically renumbered Ethics course.

No implicit cache, network call, prerequisite promotion or fresh review certificate.
The ordinary one-source pipeline cannot establish this two-source binding.
"""
from importlib import import_module
from pathlib import Path
import json

observer=import_module('atlas.adapters.mit-ai-decision-making-bs.reviewed_hass_subjects')
MANIFEST=json.loads(Path(__file__).with_name('reviewed_hass_subjects.json').read_text())
ARCHIVE_ID='mit-ai-hass-review-philosophy-renumbered-ethics-fall2009'
NUMBERING_ID='mit-ai-hass-review-philosophy-numbering'
COURSE_ID='mit-ai-hass-ethics-24-130'
REQUIRED_SOURCE_IDS=(ARCHIVE_ID,NUMBERING_ID)
SOURCES=[MANIFEST['source_specs'][sid]['url']for sid in REQUIRED_SOURCE_IDS]


def observe_sources(payloads):
    """Observe only when the caller provides both separately obtained source bodies."""
    missing=set(REQUIRED_SOURCE_IDS)-payloads.keys()
    if missing:raise ValueError('Historical Ethics requires both source payloads: '+', '.join(sorted(missing)))
    if any(not isinstance(payloads[sid],str)or not payloads[sid].strip()for sid in REQUIRED_SOURCE_IDS):
        raise ValueError('Historical Ethics source payload is empty')
    mappings=observer.observe_philosophy_numbering(payloads[NUMBERING_ID])
    relevant=[r for r in mappings if r['code']=='24.130' or r['former_code']=='24.231']
    if len(relevant)!=1 or (relevant[0]['code'],relevant[0]['former_code'],relevant[0]['title']) != ('24.130','24.231','Ethics (CI-M)'):
        raise ValueError('Exact Ethics former-number support missing or contradictory')
    return observer.observe_philosophy_renumbered_ethics(payloads[ARCHIVE_ID],payloads[NUMBERING_ID])


def parse_sources(payloads):
    found=observe_sources(payloads)
    listed=MANIFEST['courses'][COURSE_ID]
    identity=dict(id=COURSE_ID,code=listed['listed_code'],name=listed['listed_name'],source_id=listed['listed_source_id'])
    rows=[]
    for observation in found:
        review=observer.matched_review(identity,observation,SOURCES[0],MANIFEST)
        if not review:continue
        rows.append(dict(id=COURSE_ID,code=identity['code'],name=identity['name'],
                         description=review['description_summary'],prerequisites=review['prerequisites'],
                         credits=review['credits'],credit_unit='units',category=review['category'],
                         source_id=ARCHIVE_ID,url=SOURCES[0],public_site=None,syllabus=None,
                         notes=list(review['restrictions'])+[review['identity_note']]))
    return dict(id='mit-ai-decision-making-bs',courses=rows,requirements=[],
                observed_dependency_source_ids=list(REQUIRED_SOURCE_IDS))
