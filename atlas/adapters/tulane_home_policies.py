"""Scoped Tulane home-school observations, reviewed through the public reader."""
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, requirement

URLS={key:'https://catalog.tulane.edu/'+key+'/' for key in ('liberal-arts','business','public-health-tropical-medicine')}
TITLES={'liberal-arts':'School of Liberal Arts','business':'A. B. Freeman School of Business','public-health-tropical-medicine':'Celia Scott Weatherhead School of Public Health and Tropical Medicine'}
PREFIXES={'liberal-arts':['The School of Liberal Arts allows students','Individual departments may have additional restrictions'], 'business':['If a student chooses to pursue a double major within Freeman'], 'public-health-tropical-medicine':['A full description of academic policies for all students in Newcomb-Tulane College']}
HASHES={'liberal-arts': '4e36c4e6f66d6078c9318f2cb77776682efc8d413dd2b843b0e46b5e0ed7d780', 'business': '49a490f0c9d0e17b3d260aec953f584bf814bb5ae5fc95a03543552abaf68336', 'public-health-tropical-medicine': '9d0534e633e699344c8b131e91f443dcc4a1605aca31770884c91632f8107c95'}
POLICIES={
 'liberal-arts':('Liberal Arts home-school minor limits','For Liberal Arts students, the school permits one or two minors, requires at least a 2.000 minor GPA, and prohibits counting a first-minor course toward a second minor. Individual departments may add major/minor overlap restrictions; the AI Literacy minor’s own three-credit major overlap cap still applies.'),
 'business':('Freeman overlap wording — outside-school scope unresolved','Freeman prohibits double-counting in its described double-major or major/minor combinations and requires semester advising. The paragraph starts with a within-Freeman qualifier but does not explicitly explain its reach to an NTC minor. Applicability to AI Literacy versus that minor’s three-credit major overlap permission remains unresolved; neither permission nor a blanket prohibition is inferred.'),
 'public-health-tropical-medicine':('Public Health undergraduate policy referral','Public Health’s undergraduate policy section directs students to Newcomb-Tulane College academic policies. Those minor rules are already mapped. The separate graduate transfer, residency and grading rules on the same page are not applied to this undergraduate minor.'),
}

def parse_reviewed(value,*,pid,key):
    value=clean(value)
    if hashlib.sha256(value.encode()).hexdigest()!=HASHES[key]:
        raise ValueError('Tulane home-school policy changed; review required: '+key)
    title,summary=POLICIES[key]
    return dict(id=pid,curriculum_status='partial',courses=[],requirements=[requirement(pid,'home-'+key,title,pid+'-home-'+key,[],kind='note',summary=summary)])

def parse_source(html,*,pid,key):
    soup=BeautifulSoup(html,'html.parser')
    if not any(clean(h.get_text(' ',strip=True))==TITLES[key] for h in soup.find_all('h1')):raise ValueError('Tulane home-school identity changed')
    values=[]
    for prefix in PREFIXES[key]:
        matches=[clean(p.get_text(' ',strip=True)) for p in soup.find_all('p') if clean(p.get_text(' ',strip=True)).startswith(prefix)]
        if len(matches)!=1:raise ValueError('Tulane home-school policy boundary changed')
        values.extend(matches)
    return parse_reviewed(' '.join(values),pid=pid,key=key)

def register(pid,sources,parsers):
    for key,url in URLS.items():
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,key=key:parse_source(html,pid=pid,key=key)
