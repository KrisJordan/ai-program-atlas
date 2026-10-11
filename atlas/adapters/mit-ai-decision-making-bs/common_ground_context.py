"""Observe public Common Ground detail fields without resolving source precedence."""
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import rule
URL='https://computing.mit.edu/cross-cutting/common-ground-for-computing-education/common-ground-subjects/c35-c85-interactive-data-visualization-society/'
SID='mit-ai-c35-common-ground'
TITLE='C35/C85 Interactive Data Visualization and Society'


def parse(html):
    soup=BeautifulSoup(html,'html.parser');h=soup.find('h1')
    if not h or h.get_text(' ',strip=True)!=TITLE:raise ValueError('Common Ground C35 title mismatch')
    lists=[ul for ul in soup.find_all('ul')if 'Offered under:'in ul.get_text(' ',strip=True)]
    if len(lists)!=1:raise ValueError('C35 detail facts missing/ambiguous')
    fields={}
    for li in lists[0].find_all('li',recursive=False):
        label=li.find('strong')
        if label:
            key=label.get_text(' ',strip=True);fields[key]=li.get_text(' ',strip=True).removeprefix(key).strip()
    if fields.get('Offered under:')!='6.C35, 6.C85, 11.C35, 11.C85':raise ValueError('C35 detail codes changed')
    if any(not fields.get(k)for k in ['Units:','Prerequisite:','Term(s):','Level:']):raise ValueError('C35 detail scope incomplete')
    summary=(f"The public Common Ground page lists {fields['Units:']} MIT units, prerequisite {fields['Prerequisite:']}, term {fields['Term(s):']} and level {fields['Level:']} for its stated code group. "
             'Its facts provide no offering year. Preserve this source observation separately from the dated EECS annotations; it neither establishes supersession nor merges undergraduate/graduate course identities.')
    return dict(id='mit-ai-decision-making-bs',courses=[],requirements=[rule(
        'mit-ai-c35-common-ground-context','Common Ground C35/C85 source context',SID,
        ['mit-ai-6-c35-j','mit-ai-v2025-6-c35'],kind='note',summary=summary)])


SOURCE_PARSERS={URL:parse}
