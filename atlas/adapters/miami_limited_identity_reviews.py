"""Conservative observations for exact dated identities without current descriptions.

Manual review is stored in the companion manifest and curated seeds only. This
helper never emits category_review and never supplies unavailable course facts.
"""
import json
from pathlib import Path

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def apply_observed_categories(result):
    for record in result.get('courses', []):
        entry = SPEC['courses'].get(record['code'])
        if entry is None or record.get('source_id') != entry['source_id']:
            continue
        if record.get('name') != entry['name']:
            raise ValueError('Miami limited identity title changed; fresh review required')
        if record.get('description') or record.get('prerequisites'):
            raise ValueError('Miami limited identity gained content; fresh review required')
        record['category'] = entry['category']
    return result
