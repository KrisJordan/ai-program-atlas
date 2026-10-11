"""Dated annotation observations for exact, separately retained chart references.

The original chart parser cannot supply these fields. Only a fresh observation of
its explicitly matched departmental annotation can activate this supplemental
metadata; the source occurrence and requirement roles are never merged.
"""
import json
from pathlib import Path

REVIEWS = json.loads(Path(__file__).with_name('reviewed_reference_annotations.json').read_text())


def observe(parsed):
    """Return bounded reference metadata only for an unchanged full annotation."""
    by_code = {c['code']: c for c in parsed['courses']}
    digests = parsed.get('observed_core_description_digests', {})
    result = []
    for cid, review in REVIEWS.items():
        actual = by_code.get(review['observed_code'])
        if not actual or actual['name'] != review['observed_name']:
            continue
        if digests.get(actual['id']) != review['annotation_digest']:
            continue
        # Explicitly bounded designation normalization, never fuzzy identity.
        if review['reference_code'].replace('[J]', '') != actual['code']:
            continue
        if review['reference_name'].removesuffix(' (CI-M)') != actual['name']:
            continue
        result.append(dict(
            id=cid, code=review['reference_code'], name=review['reference_name'],
            description=review['description_summary'],
            prerequisites=actual['prerequisites'],
            credits=None if review['withhold_credits'] else actual['credits'],
            credit_unit=actual['credit_unit'], category=review['category'],
            source_id=actual['source_id'], url=actual['url'],
            public_site=actual['url'], syllabus=None, notes=list(review['notes']),
        ))
    return result


def with_annotations(primary):
    def parse(html):
        result = primary(html)
        result['courses'].extend(observe(result))
        return result
    return parse
