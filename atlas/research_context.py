"""Presentation-only CSRankings context; never compute or reorder research ranks.

Numeric meaning and institution matching belong to the source-backed importer.
Missing rows/statuses never become zero, last place, or curriculum quality.
"""
import math

FIELDS = {
    'ai': 'Artificial intelligence',
    'vision': 'Computer vision',
    'mlmining': 'Machine learning & data mining',
    'nlp': 'Natural language processing',
    'inforet': 'Information retrieval',
    'aggregate': 'Five-field aggregate',
}
MISSINGNESS = {
    'observed': 'Observed',
    'no_selected_output': 'No selected publication output',
    'not_listed': 'Institution not listed in snapshot',
    'outside_eligible': 'Outside eligible research population',
    'unmatched': 'Institution match unresolved',
    'source_missing': 'Source observation unavailable',
    'permission_required': 'Reuse permission unresolved',
}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def institution_context(data, institution_id):
    cs=data.get('csrankings') or {}
    method=cs.get('methodology') or {}
    available=isinstance(method,dict) and method.get('status')=='available'
    if not available:
        return None
    observations={row.get('field'):row for row in cs.get('observations',[]) if row.get('institution_id')==institution_id}
    population=(cs.get('population') or {}).get('ranked_institutions_by_field') or {}
    rows=[]
    for field,label in FIELDS.items():
        observation=observations.get(field,{})
        status=observation.get('missingness') or 'source_missing'
        observed=status=='observed' and number(observation.get('value'))
        rank=observation.get('rank')
        # An invalid observed number cannot smuggle an ordinal rank into the UI.
        rank_text=f'#{rank}' if observed and isinstance(rank,int) and not isinstance(rank,bool) and rank>0 else 'Not ranked in this selection'
        if observed and rank_text.startswith('#') and isinstance(population.get(field),int):
            rank_text += ' of ' + str(population[field])
        adjusted=observation.get('adjusted_count')
        rows.append({'field':field,'label':label,'missingness':status,
                     'status_label':MISSINGNESS.get(status,'Source status not recognized'),
                     'score_text':f"{observation['value']:.1f}" if observed else 'Not available',
                     'rank_text':rank_text,
                     'adjusted_count_text':f'{adjusted:.3f}' if observed and number(adjusted) and field!='aggregate' else 'Not applicable' if field=='aggregate' else 'Not available'})
    return {'year_start':method.get('year_start'),'year_end':method.get('year_end'),
            'source_url':method.get('source_url'),'source_snapshot':method.get('source_snapshot'),
            'upstream_institution':next((r.get('upstream_institution') for r in observations.values() if r.get('upstream_institution')),None),
            'rows':rows}


def aggregate_rank_map(csrankings):
    """Use only available observed aggregate ranks; never manufacture missing ranks."""
    if (csrankings.get('methodology') or {}).get('status') != 'available':
        return {}
    result = {}
    seen = set()
    for row in csrankings.get('observations', []):
        if row.get('field') != 'aggregate':
            continue
        iid, rank, score = row.get('institution_id'), row.get('rank'), row.get('value')
        valid = (row.get('missingness') == 'observed' and number(score) and score > 0
                 and isinstance(rank, int) and not isinstance(rank, bool) and rank > 0)
        if iid in seen:
            result[iid] = None
        else:
            result[iid] = rank if valid else None
        seen.add(iid)
    return result
