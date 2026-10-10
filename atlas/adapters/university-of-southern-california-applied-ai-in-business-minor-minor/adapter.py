"""USC minor identity and Marshall-wide policies; catalog curriculum inaccessible."""
from atlas.adapters.discovery_common import parse_identity
from atlas.adapters.national_curriculum_common import content, require_phrases, rule

PROGRAM_ID='university-of-southern-california-applied-ai-in-business-minor-minor'
SOURCES=(
 'https://www.marshall.usc.edu/news/usc-marshall-launches-applied-ai-and-business-minor',
 'https://students.marshall.usc.edu/current-students/applying-marshall-current-usc-students/marshall-minors',
)


def parse(html):
    result=parse_identity(html,program_id=PROGRAM_ID,title='Applied AI in Business',award='minor',kind='minor',aliases=(),award_terms=())
    root=content(html,'USC Marshall Launches Applied AI in Business Minor')
    require_phrases(root,['launching a new Applied AI in Business minor in Fall 2026','responsible use of technology, entrepreneurship, digital media and communications, product management, and leadership techniques'])
    result['outcomes']=[dict(text='Apply AI to business decisions and collaborative innovation, with attention to responsible technology use, entrepreneurship, communications, product management and leadership.',kind='source_stated',source_id=PROGRAM_ID+'-official',locator='Program announcement; curriculum and career-readiness discussion')]
    return result


def parse_policies(html):
    root=content(html,'Marshall Minors');sid=PROGRAM_ID+'-admission'
    links=[a for a in root.find_all('a') if a.get_text(' ',strip=True)=='Applied AI in Business Minor']
    if not links:raise ValueError('Named AI minor absent from applicable minor list')
    require_phrases(root,['completion of 32-48 units, a declared major, and a minimum USC GPA of 2.75','maximum of three Marshall courses prior to admission','Applications to Marshall minors are accepted throughout the year','all the necessary prerequisites for each course','without pre-requisite waivers, course substitutions or exceptions','minimum of 16 unique units outside of your home academic department','Students admitted to a Marshall minor are admitted to the current Catalogue year','with some exceptions depending on your specific program of study'])
    specs=[('admission','Marshall minor admission','Admission requires a declared major, completion of 32–48 units and a USC GPA of at least 2.75. Applications are accepted throughout the year.'),('preadmission','Courses before admission','Students may take at most three Marshall courses before minor admission.'),('prerequisites','Prerequisites and substitutions','Complete every course prerequisite. Minor requirements follow the USC Catalogue without prerequisite waivers, substitutions or exceptions.'),('unique','Unique units','At least 16 unique units must be outside the student’s home academic department. This is a common minor rule, not a verified total for this minor.'),('catalogue','Applicable catalog year','Students enter under the catalog year current at admission, and that year’s requirements appear on their STARS report.'),('eligibility','Marshall-major eligibility and overlap','Business Administration and Accounting majors may apply, subject to exceptions for their specific major, emphasis or joint program. Consult the published eligibility list and an advisor about overlap restrictions.')]
    return dict(id=PROGRAM_ID,requirements=[rule(PROGRAM_ID+'-'+key,title,sid,kind='note',summary=summary) for key,title,summary in specs])


SOURCE_PARSERS={SOURCES[0]:parse,SOURCES[1]:parse_policies}
