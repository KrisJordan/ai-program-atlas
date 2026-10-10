"""Visit-verified course resources; term-specific examples are not current catalog rules."""
import hashlib
import re
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, text

RESOURCES = {
 'https://www.cs.cmu.edu/~07280/': dict(code='07-280',name='Artificial Intelligence and Machine Learning I',term='Fall 2026',source='cmu-07280-fall-2026-site',syllabus=False),
 'https://www.cs.cmu.edu/~07380': dict(code='07-380',name='Artificial Intelligence and Machine Learning II',term='Fall 2026',source='cmu-07380-fall-2026-site',syllabus=False),
 'https://amirsoofi.github.io/11411-NLP-Spring2026/': dict(code='11-411',name='Natural Language Processing',term='Spring 2026',source='cmu-11411-spring-2026-site',syllabus=False),
 'https://amirsoofi.github.io/11411-NLP-Spring2026/syllabus': dict(code='11-411',name='Natural Language Processing',term='Spring 2026',source='cmu-11411-spring-2026-syllabus',syllabus=True),
 'https://www.cs.cmu.edu/~16385/': dict(code='16-385',name='Computer Vision',term='Spring 2020',source='cmu-16385-spring-2020-site',syllabus=True),
}


def parse_resource(html, *, pid, url):
    config=RESOURCES[url];soup=BeautifulSoup(html,'html.parser')
    for el in soup.find_all(['script','style']):el.decompose()
    value=text(soup)
    if soup.find('input',attrs={'type':'password'}) or re.search(r'^(?:Access denied|Sign in|Just a moment)',(text(soup.title) if soup.title else ''),re.I):raise ValueError('Protected course resource is not evidence')
    identity = any(config['code'] in text(h) for h in soup.find_all(['h1','h2','title'])) or re.search(r'Course Title:\s*'+re.escape(config['code']),value)
    if not identity or config['term'] not in value:raise ValueError('Course identity or expected offering term changed')
    if config['syllabus'] and 'syllabus' not in value.lower():raise ValueError('Syllabus section missing')
    c=course(config['code'],config['name'],config['source'],url,category='ai_ml')
    c['public_site']=url if not url.endswith('/syllabus') else None
    if config['syllabus']:c['syllabus']=url
    return dict(id=pid,curriculum_status='partial',courses=[c],requirements=[],observed_resource_digest=hashlib.sha256(value.encode()).hexdigest(),notes=[config['term']+' course resource only. Catalog credits and prerequisites remain separate; no automatic requirement or freshness certification.'])


def register(pid,sources,parsers):
    for url in RESOURCES:
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,url=url:parse_resource(html,pid=pid,url=url)
