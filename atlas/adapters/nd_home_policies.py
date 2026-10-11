"""Conditional home-college observations for the all-majors AI Essentials minor."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, requirement

URLS = {key: 'https://catalog.nd.edu/undergraduate/'+key+'/' for key in ('arts-letters','engineering','science')}
TITLES = {'arts-letters':'College of Arts and Letters','engineering':'College of Engineering','science':'College of Science'}
PREFIXES = {
 'arts-letters': [('p','Students may not cross-count a single course'),('p','With permissions from the academic dean')],
 'engineering': [('p','This policy applies to academic programs contained within the college of engineering.')],
 'science': [('p','Each College of Science student must enroll'),('p','Listed below are the allowed options'),('p','Students pursuing one of the above combination programs'),('p','Note : Courses may only be counted once'),('li','University and core requirements'),('li','College and primary major requirements'),('li','Any other program (second major')],
}
HASHES = {'arts-letters': '29ff57722f79e64118afa150ab403288389b295e4cea273aea1efebafe2a2afb', 'engineering': '770f71c490418411c4060717043f0b47b548a19a4efdf9c08e4933018ef60e4f', 'science': 'cda621666e9755e7e35f66e7f78fbc7089c70227b5a611db1e221276ba29923a'}
POLICIES = {
 'arts-letters': [('overlap','Arts and Letters home-college overlap — reconciliation needed','For Arts and Letters students, the college describes replacing a shared program requirement with an approved course and retaining five unique minor courses/15 credits. University/college requirements may still overlap. The AI Essentials page separately allows three major credits to overlap; the public sources do not explain how that permission interacts with this college baseline. A joint approved exception is not inferred.'),('grading','Arts and Letters home-college grading','The Arts and Letters elective pass/fail option requires dean permission and junior/senior standing. It excludes courses in declared major, supplementary-major or minor disciplines and university/college core requirements. This is a home-college condition, not permission to use pass/fail in this minor.')],
 'engineering': [('scope','Engineering students taking an outside-college credential','Engineering explicitly limits its internal multi-counting rule to Engineering programs. An outside-college secondary credential follows its home college’s policies or an agreement between the colleges; questions go to the Associate Dean for Undergraduate Programs. Engineering’s internal unlimited overlap rule is not applied to this Mendoza minor.')],
 'science': [('approval','Science home-college approval and completion','Science expressly includes Mendoza minors among cross-college combinations. Program directors and the Science dean must formally accept the combination; substantial overlap prevents approval. Changes to a minor are generally expected not to extend study beyond eight semesters or require an overload.'),('unique','Science home-college uniqueness and counting','For Science students, a course may count once at each listed tier: university/core; college/primary major; and other programs, subject to the stated exception for a defined Science program. Each program must have at least 50% unique courses. This condition supplements the AI minor’s own overlap limit; it is not a new universal credit minimum.')],
}

def observed_text(html, key):
    soup = BeautifulSoup(html, 'html.parser')
    if not any(clean(h.get_text(' ',strip=True))==TITLES[key] for h in soup.find_all('h1')):
        raise ValueError('Notre Dame home-college identity changed: '+key)
    values=[]
    for tag,prefix in PREFIXES[key]:
        matches=[clean(p.get_text(' ',strip=True)) for p in soup.find_all(tag) if clean(p.get_text(' ',strip=True)).startswith(prefix)]
        if len(matches)!=1:raise ValueError('Notre Dame policy boundary changed: '+prefix)
        values.extend(matches)
    return '\n'.join(values)

def parse_source(html, *, pid, key):
    value=observed_text(html,key)
    if hashlib.sha256(value.encode()).hexdigest()!=HASHES[key]:
        raise ValueError('Notre Dame home-college policy changed; review required: '+key)
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[requirement(pid,'home-'+key+'-'+suffix,title,pid+'-home-'+key,[],kind='note',summary=summary) for suffix,title,summary in POLICIES[key]])

def register(pid,sources,parsers):
    for key,url in URLS.items():
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,key=key:parse_source(html,pid=pid,key=key)
