"""Observe titles for existing handbook identities without importing eligibility."""
import json
from .common import penn_course
from .linked_policies import PID, INVENTORY, parse_technical_inventory

# These identities already occur in the handbook's classification/context lists.
# Their JSON rows may supply names even when not approved as technical electives.
HANDBOOK_IDENTITIES = frozenset({
    'BEPP 2010', 'BEPP 2200', 'BEPP 2330', 'BEPP 2610', 'BEPP 2840',
    'EAS 2030', 'OIDD 2900', 'CIS 1060', 'ECON 0620', 'CIS 1070',
    'EAS 5950', 'IPD 5090', 'LGST 2220', 'LGST 2440', 'MGMT 2370',
    'MGMT 2640', 'OIDD 2360', 'OIDD 2550', 'OIDD 3140', 'OIDD 3150',
})


def parse_inventory_with_titles(raw):
    observed = parse_technical_inventory(raw)  # Validate every row/status first.
    known = {c['code'] for c in observed['courses']}
    for row in json.loads(raw):
        if row['course4d'] not in HANDBOOK_IDENTITIES or row['course4d'] in known:
            continue
        course = penn_course(row['course4d'], row['title'], PID + '-technical-inventory', INVENTORY, category='other')
        course['notes'] = ['Title metadata only: the current technical-elective status is no. This observation does not establish eligibility or a requirement.']
        observed['courses'].append(course)
    return observed
