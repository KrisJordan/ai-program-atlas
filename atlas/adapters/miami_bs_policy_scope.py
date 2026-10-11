"""Preserve program requirements above a college minimum without a false conflict."""
from atlas.adapters.national_curriculum_common import rule

PROGRAM='miami-data-science-ai-bs'
SUMMARY=('The BS curriculum publishes nine credits of language study at the 200 level or higher and a '
         '121-credit total. These program facts are compatible with the college’s at-least-three-credit '
         'language minimum and the university’s at-least-120-credit graduation minimum. A sample plan '
         'does not override the requirements table. Published college language waivers retain their own '
         'conditions; this comparison does not establish that a waiver removes every credit in the '
         'program’s nine-credit row or grant an individual exemption.')


def apply(observed):
    if observed.get('id')!=PROGRAM:raise ValueError('Unreviewed Miami BS scope')
    rows=observed.get('requirements',[])
    language=[r for r in rows if r['title']=='Language course 200-level or higher']
    total=[r for r in rows if r['title']=='Total Credit Hours']
    if len(language)!=1 or language[0]['credits']!=9 or len(total)!=1 or total[0]['credits']!=121:
        raise ValueError('Miami BS published language/total requirement changed; review required')
    rid=PROGRAM+'-language-conflict'
    if any(r['id']==rid for r in rows):raise ValueError('Duplicate Miami BS scope note')
    return {**observed,'requirements':rows+[rule(rid,'Program language and credit requirements exceed general minima',PROGRAM+'-catalog',kind='note',summary=SUMMARY)]}
