"""Index same-source contextual groups by exact option-route membership.

These are reading aids, never new requirements, ancestry or course-count rules.
"""
from collections import defaultdict


def related_option_groups(requirements):
    children=defaultdict(list)
    for r in requirements:children[r.get('parent_id')].append(r)
    def routes(r):
        direct={frozenset([cid]) for cid in r.get('course_ids',[])}
        for child in children[r['id']]:
            if child.get('kind')!='all' or not child.get('course_ids') or children[child['id']]:return set()
            direct.add(frozenset(child['course_ids']))
        return direct
    result={}
    for pool in requirements:
        if pool.get('kind') not in {'choose_courses','alternative'} or not pool.get('source_id'):continue
        options=routes(pool)
        if not options:continue
        groups=[]
        for group in children[pool.get('parent_id')]:
            if group.get('kind')!='note' or group.get('course_ids') or group.get('source_id')!=pool['source_id'] or not children[group['id']]:continue
            members=routes(group)
            if members and members<=options:groups.append(group)
        if groups:result[pool['id']]=groups
    return result
