"""Miami cognate and language-placement observations; no completeness inference."""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, content, course, rule

COGNATES = 'https://cognates.miami.edu/'
INDIVIDUALIZED = 'https://cognates.miami.edu/courses/individualized'
LANGUAGES = 'https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/modern-languages-literatures/'
SOURCES = [COGNATES, INDIVIDUALIZED, LANGUAGES]
SOURCE_IDS = {'cognates':'miami-cognates-supplement', 'individualized':'miami-individualized-cognates', 'languages':'miami-language-placement'}
TITLES = {'cognates':'About Cognates', 'individualized':'Individualized Cognate Courses', 'languages':'Modern Languages and Literatures'}


def observed_text(html, key):
    root = content(html, TITLES[key])
    text = clean(root.get_text(' ', strip=True))
    if key == 'languages':
        start, end = text.find('Placement Guidelines for MLL Courses'), text.find('Advanced Writing and Communication Requirement')
        if start < 0 or end <= start: raise ValueError('Language placement boundaries missing')
        text = text[start:end]
        blocks = [clean(c.get_text(' ',strip=True)) for c in root.select('.courseblock')
                  if re.match(r'SPA (107|207|208|307)\.',clean(c.get_text(' ',strip=True)))]
        if len(blocks) != 4: raise ValueError('Expected four named heritage course records')
        text += ' ' + ' '.join(blocks)
    return text


POLICIES = {'cognates': [('cognate-selection', 'Student-selected cognates and declaration', 'A cognate has at least three courses and nine credits. Students select their cognates and declare them through their home college by the end of sophomore year. A major/minor does not prescribe a specific cognate outside its own Area of Knowledge; thematic substitutions require responsible-unit approval.')], 'individualized': [('individualized-overlap', 'Individualized cognate restrictions', 'Each individualized cognate needs at least three courses and nine credits with the same Area of Knowledge attribute in CaneLink. Its courses cannot also fulfill any other degree requirement, including quantitative proficiency. CR grades are excluded except eligible test credit with a specific Miami equivalency. This stricter statement is specific to individualized cognates, not a prohibition on all thematic cognate/major relationships.')], 'languages': [('language-diagnostic', 'Language placement is assessed individually', 'Published placement guidelines are provisional: the instructor conducts a first-day diagnostic and assigns the appropriate course or track. Native speakers of French, German, Italian, Portuguese or Spanish cannot enter 101/102/105/201/202/203/301 in that language. Native Spanish speakers educated in Spanish-language high schools begin with SPA 302,303 or307.'), ('spanish-heritage', 'Spanish heritage placement routes', 'Spanish heritage learners must enter SPA 107,207,208 or307 according to preparation and assessment, rather than the second-language track. SPA 107 is a preparatory 100-level course; it alone does not meet the college 200-level language requirement. SPA 207 follows SPA 107 or at least two high-school years; SPA 208 corresponds to four years, AP Language 5 or AP Literature 4; direct 307 placement is described for AP Literature 5. SPA 107/207/208 exclude graduates of Spanish-language high schools.'), ('language-transfer', 'Other-language equivalence and level', 'For a language not taught at Miami, the department may approve an accredited outside course and its transfer equivalency. The published language requirement needs 300-level equivalency for a native speaker or200-level for a second-language learner. Program-specific higher credit requirements remain controlling; no additional waiver of those credits is inferred from a general college minimum.')]}

HASHES = {'cognates': '2e33b60c219cbad7409e96a877e59d39e034a8d23058b5d98ed89b6a992d6c2e', 'individualized': 'b1d5f8a8c76656433600c17e48d63a06549d30b6df483673180c700a8ce3e43c', 'languages': 'f81925d7a7ecbccf91359098f9eabb5df3e3baada6e772284a7fe7f60521ab2d'}

DESCRIPTIONS = {
 '107':'Develops speaking, reading and writing for heritage learners with passive Spanish knowledge.',
 '207':'Develops communication skills for heritage learners with some prior instruction and functional Spanish.',
 '208':'Develops formal Spanish speaking and literacy for heritage learners with functional communication skills.',
 '307':'Analyzes Spanish-language literary and cultural works, with critical writing for heritage and native speakers.'}


def parse_source(html, *, pid, key):
    text = observed_text(html, key)
    if hashlib.sha256(text.encode()).hexdigest() != HASHES[key]:
        raise ValueError('Miami supplementary source changed; review required: '+key)
    sid = SOURCE_IDS[key]
    requirements = [rule(pid+'-supplement-'+suffix, title, sid, kind='note', summary=summary)
                    for suffix,title,summary in POLICIES[key]]
    result = dict(id=pid, requirements=requirements)
    if key == 'languages':
        courses=[]
        soup=BeautifulSoup(html,'html.parser')
        for block in soup.select('.courseblock'):
            value=clean(block.get_text(' ',strip=True))
            match=re.match(r'SPA (107|207|208|307)\. (.+?)\. (\d+) Credit Hours\.',value)
            if not match: continue
            number,name,amount=match.groups()
            c=course(pid,'SPA '+number,name,sid,LANGUAGES,float(amount),'semester_hours',category='human_context')
            c['description']=DESCRIPTIONS[number]
            if number=='307':c['prerequisites']='SPA 208. Credit cannot be earned for both SPA 301 and SPA 307 (formerly 343).'
            courses.append(c)
        result['courses']=courses
        requirements[1]['course_ids']=[c['id'] for c in courses]
    return result


def register(pid, sources, parsers, *, arts=False):
    for key,url in [('cognates',COGNATES),('individualized',INDIVIDUALIZED)]+([('languages',LANGUAGES)] if arts else []):
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,key=key:parse_source(html,pid=pid,key=key)
