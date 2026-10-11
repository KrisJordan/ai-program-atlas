"""Keep enrollment, credit acceptance and preapproval scope distinct."""
import hashlib
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean
from atlas.adapters.national_curriculum_common import rule
from atlas.adapters.miami_policies import SPECS, parse_policy

PROGRAMS={
    'university-of-miami-artificial-intelligence-for-business-technology-minor-minor',
    'miami-data-science-ai-bs', 'miami-ai-technologies-business-bsba',
    'university-of-miami-data-science-and-artificial-intelligence-ba-degree',
    'university-of-miami-artificial-intelligence-technologies-for-business-other-degree',
}
URL=SPECS['transfer'][0]
DIGEST='92af5960f62d0ff74b3b202432111a355e9f418ee58a0d86c3b5439efe30c9e6'
SUMMER=('The general concurrent-enrollment prohibition excludes summer, but this does not grant transfer credit. '
        'The separate Courses Not Accepted rule rejects outside coursework while actively enrolled at Miami, '
        'including a Miami summer Session A course and an outside Session B course. Concurrent outside summer '
        'courses also cannot receive Miami-administered federal, state or institutional financial aid. '
        'Enrollment, transfer-credit acceptance and aid eligibility are distinct rules, not contradictory grants '
        'and denials of the same permission. Applicable business residency restrictions remain separate.')
PROCESS=('Outside coursework must follow the MATES transfer evaluation process; requests do not go directly '
         'to individual departments. Future-course requests should be submitted during the preceding semester, '
         'and the university reserves the right to reject courses taken without preapproval. A preapproved '
         'equivalence remains subject to transfer policy and the college’s degree-applicability decision. '
         'Continuing students must submit the official transcript by the end of the following semester, and '
         'incoming students by the end of their first semester. Transfer grades do not enter the regular Miami '
         'GPA, although Latin-honors calculations use them. Existing accepted transfer/test equivalents cannot '
         'ordinarily be repeated; a specified-program test-credit exception removes the examination credit first.')


def parse(html, *, pid):
    if pid not in PROGRAMS:
        raise ValueError('Unreviewed Miami transfer degree scope')
    result=parse_policy(html,pid=pid,code='transfer')
    soup=BeautifulSoup(html,'html.parser');root=soup.find(id='content')
    for nav in root.select('nav'):nav.decompose()
    if hashlib.sha256(clean(root.get_text(' ',strip=True)).encode()).hexdigest()!=DIGEST:
        raise ValueError('Miami transfer conditions changed; renewed source review required')
    sid='miami-transfer-policy'
    result['requirements']=[
        rule(pid+'-policy-summer-transfer-conflict','Summer enrollment, transfer credit and aid have different scopes',sid,kind='note',summary=SUMMER),
        rule(pid+'-policy-transfer-process','Transfer evaluation and document deadlines',sid,kind='note',summary=PROCESS),
    ]
    return result


def register(pid,sources,parsers):
    if pid not in PROGRAMS:raise ValueError('Unreviewed Miami transfer scope')
    if URL not in sources:sources.append(URL)
    parsers[URL]=partial(parse,pid=pid)
