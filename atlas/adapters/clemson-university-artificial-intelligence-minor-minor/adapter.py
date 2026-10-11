"""Observe the department's minimum; blocked catalog coverage stays unresolved."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import requirement,clean
PROGRAM_ID='clemson-university-artificial-intelligence-minor-minor'
SOURCES=('https://www.clemson.edu/cecas/departments/computing/academics/undergrad/degrees/',)
SOURCE_ID='clemson-ai-minor-department'
def parse(html: str)->dict:
    soup=BeautifulSoup(html,'html.parser')
    h=next((x for x in soup.find_all('h2') if clean(x.get_text())=='Artificial Intelligence'),None)
    if not h:raise ValueError('AI minor heading missing')
    text=clean(h.find_next('p').get_text())
    m=re.search(r'minor in Artificial Intelligence requires a minimum of (\d+) credits',text)
    if not m:raise ValueError('Minor minimum changed or missing')
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',curriculum_status='partial',courses=[],requirements=[requirement(PROGRAM_ID,'minimum','Published credit minimum',SOURCE_ID,[],kind='note',credits=int(m[1]),summary='Minimum '+m[1]+' published credits, including programming fundamentals and statistical foundations; individual courses and normalized credit unit remain unverified.')])


FAQ_URL = 'https://www.clemson.edu/cecas/departments/computing/students/advising/faq.html'
FAQ_SOURCE = 'clemson-computing-advising-faq'
SOURCES += (FAQ_URL,)

def parse_advising_faq(html):
    from atlas.adapters.national_curriculum_common import content, require_phrases, rule
    root = content(html, 'Advising FAQ')
    require_phrases(root, ['Check your undergraduate announcements', 'Generally, if a CPSC course', 'general electives', 'retake that class for a C or higher', 'For non-CPSC-prefixed courses', 'Transfer Course Equivalency List', 'Approval of Coursework to be Taken Elsewhere', 'For CPSC-prefixed coursework', 'Dr. Plaue', 'printout of the syllabus', 'prior to taking a class at another institution'])
    return dict(id=PROGRAM_ID, requirements=[
        rule('clemson-ai-cpsc-grade-guidance', 'CPSC grade guidance; minor-specific policy unresolved', FAQ_SOURCE, kind='note', summary='Computing advising generally requires C or better when a CPSC course serves a degree requirement other than general electives, and directs students to the undergraduate announcements. This guidance does not establish this minor’s exact grade or GPA rules.'),
        rule('clemson-ai-external-course-review', 'Prior review of external coursework', FAQ_SOURCE, kind='note', summary='Before taking outside coursework, obtain the Elsewhere form and advisor approval; use the transfer-equivalency list for non-CPSC courses. For CPSC-equivalent work, arrange the named computing review and supply the syllabus. This process does not itself grant minor credit.')])

SOURCE_PARSERS = {SOURCES[0]: parse, FAQ_URL: parse_advising_faq}
