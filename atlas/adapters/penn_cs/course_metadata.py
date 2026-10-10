"""Public Penn course metadata observations, with exact identities and offering terms."""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.penn_bse.common import penn_course,text

RESOURCE_SPECS={
 'https://www.engineering.upenn.edu/~cis5190/fall2026/index.html':dict(codes=['CIS 4190','CIS 5190'],name='Applied Machine Learning',identity=r'CIS\s+4190/5190',term='Fall 2026',source='penn-cis4190-5190-fall-2026',syllabus=True,prerequisite='paragraph'),
 'https://www.engineering.upenn.edu/~jyzh/courses/cis5210/26su/':dict(codes=['CIS 5210'],name='Artificial Intelligence',identity=r'cis5210-26su',term='2026 Summer',source='penn-cis5210-summer-2026-site',syllabus=False),
 'https://www.engineering.upenn.edu/~jyzh/courses/cis5210/26su/syllabus/':dict(codes=['CIS 5210'],name='Artificial Intelligence',identity=r'CIS 5210 - Artificial Intelligence',term='cis5210-26su',source='penn-cis5210-summer-2026-syllabus',syllabus=True,prerequisite='definition'),
 'https://machine-learning-upenn.github.io/':dict(codes=['CIS 5200'],name='Machine Learning',identity=r'CIS 5200 Machine Learning',term='Spring 2023',source='penn-cis5200-spring-2023-site',syllabus=False),
 'https://artificial-intelligence-class.org/':dict(codes=['CIS 4210'],name='Artificial Intelligence',identity=r'CIS 4210/5210 - Artificial Intelligence',term='Fall 2022',source='penn-cis4210-fall-2022-site',syllabus=False),
}
WHARTON={
 'https://statistics.wharton.upenn.edu/programs/undergraduate/course-descriptions/':dict(code='STAT 4230',source='penn-stat4230-department-description'),
 'https://lgst.wharton.upenn.edu/programs/undergraduate/course-descriptions/':dict(code='LGST 2420',source='penn-lgst2420-department-description'),
}


def root(html):
    soup=BeautifulSoup(html,'html.parser')
    if soup.find('input',attrs={'type':'password'}) or any(re.search(r'^(?:Sign in|Log in|Access denied|Just a moment|Robot verification)',text(h),re.I) for h in soup.find_all(['title','h1'])):raise ValueError('Protected page is not course evidence')
    for node in soup.find_all(['script','style']):node.decompose()
    return soup


def parse_resource(html, *, pid, url):
    config=RESOURCE_SPECS[url];soup=root(html);value=text(soup)
    if not re.search(config['identity'],value,re.I) or config['term'] not in value:raise ValueError('Penn course identity or offering changed')
    prerequisite=None
    if config.get('prerequisite')=='paragraph':
        block=next((p for p in soup.find_all('p') if text(p).startswith('Prerequisites:')),None)
        if block is None:raise ValueError('Applied ML prerequisite paragraph missing')
        prerequisite=text(block).removeprefix('Prerequisites:').strip()
    elif config.get('prerequisite')=='definition':
        match=re.search(r'Prerequisites & recommended background knowledge (.+?) Instructor ',value)
        if not match:raise ValueError('AI syllabus prerequisite definition missing')
        prerequisite=match[1]
    if config['syllabus'] and 'syllabus' not in value.lower():raise ValueError('Penn syllabus identity missing')
    courses=[]
    for code in config['codes']:
        c=penn_course(code,config['name'],config['source'],url)
        c.update(prerequisites=prerequisite,public_site=None if url.endswith('/syllabus/') else url,syllabus=url if config['syllabus'] else None)
        courses.append(c)
    return dict(id=pid,curriculum_status='partial',courses=courses,requirements=[],observed_resource_digest=hashlib.sha256(value.encode()).hexdigest(),notes=[config['term']+' resource only; historical sites do not certify current prerequisites. Individual credits are not inferred from requirement slots.'])


def parse_wharton(html, *, pid, url):
    config=WHARTON[url];soup=root(html);code=config['code'];found=[]
    for block in soup.find_all('div',class_='wfpCourseDescriptions-course'):
        h=block.find('h3')
        if not h:continue
        label=text(h);match=re.match(r'([A-Z]+)(\d{4})\s*-\s*(.+?)(?:\s*\(Course Syllabus\))?$',label)
        if not match or match[1]+' '+match[2]!=code:continue
        c=penn_course(code,match[3],config['source'],url)
        paragraphs=[text(p) for p in block.find_all('p')]
        prerequisites=[p.split(':',1)[1].strip() for p in paragraphs if p.startswith('Prerequisites:')]
        if len(prerequisites)>1:raise ValueError('Repeated Wharton prerequisite block')
        c['prerequisites']=prerequisites[0] if prerequisites else None
        if c['prerequisites'] and any('concurrently' in p and 'instructor permission' in p for p in paragraphs):c['prerequisites']+='; may be taken concurrently with instructor permission.'
        # A syllabus link in a directory is not itself visited syllabus evidence.
        found.append((c,hashlib.sha256(' '.join(paragraphs).encode()).hexdigest()))
    if len(found)!=1:raise ValueError('Expected exact Wharton course block missing or duplicated')
    return dict(id=pid,curriculum_status='partial',courses=[found[0][0]],requirements=[],observed_description_digest=found[0][1],notes=['Department course description and prerequisites only. Absent prerequisites and unvisited syllabus contents remain unknown.'])


def register_resources(pid,sources,parsers):
    for url in RESOURCE_SPECS:
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,url=url:parse_resource(html,pid=pid,url=url)


def register_wharton(pid,sources,parsers):
    for url in WHARTON:
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,url=url:parse_wharton(html,pid=pid,url=url)
