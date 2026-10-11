"""Actual public course-detail observations; changed descriptions require re-review."""
import hashlib
import re
from functools import partial
from atlas.adapters.national_curriculum_common import content, clean, course

PID = 'university-of-south-florida-artificial-intelligence-bs-degree'
BASE = 'https://cloud.usf.edu/academic-programs/details/prefix/CAI/code/'
# Reviewed source-description digests pair paraphrases with their exact observed text.
REVIEWED = {'1000': ('08df6f2cb89d05308b6f854045dc387f6f54bfaa82ea5ccbe64285ef25230ce8',
          'Introduces AI vocabulary, capabilities, limitations and '
          'applications in nontechnical terms.'),
 '2001': ('160feedf8f686560c49a32f18001c8c43eb52eb8321c6838c724e29fcfc21f7a',
          'Builds AI applications with low-code or no-code tools, '
          'language-model workflows, retrieval and agents; team projects '
          'evaluate performance, cost and responsible use.'),
 '4002': ('e95b4f9ebb5b18036e65de73fdb07914777edf06e549f8803a52c16540e5931b',
          'Introduces AI methods and software for search, reasoning and '
          'learning, including basic machine learning.'),
 '4024': ('e0fbb8bdb391f13ed875bcd903eab7f4d4e55537a37df504cfba38f6f968edda',
          'Examines professional and ethical responsibilities in AI through '
          'developing and presenting responses to real-world problems.'),
 '4105': ('8775721ae61e10d909c8b4ebbec104ffb05681315b36cd7d2c8c18dcac7be586',
          'Surveys supervised, unsupervised, reinforcement and deep learning, '
          'emphasizing evaluation and responsible practice.'),
 '4203': ('9a2c74cbab7d081f85b110e20fc7bda669d4afd02efcba0b0be0547d2fec5e5f',
          'Covers neural-network mathematics, single- and multilayer models, '
          'applications and ethical concerns.'),
 '4624': ('89f417580301898fe5a8e81ede4a854eb32477c5be2f2e641164d28a98c8e3a1',
          'Studies AI training/deployment infrastructure, frameworks, data '
          'pipelines, distributed systems and cloud scaling through practical '
          'system design.'),
 '4841': ('9634f6951167f034adefba288150a7e27ec325ff21750a2f6f9099f96fdb8304',
          'Introduces image formation and segmentation, feature matching, '
          'shape and texture analysis, object recognition and changing '
          'scenes.')}

def parse_course(html, number):
    root=content(html, 'Course Details')
    h=next((h for h in root.find_all('h2') if clean(h.get_text()).startswith('CAI '+number+':')),None)
    if not h:raise ValueError('Expected CAI course identity missing')
    name=clean(h.get_text()).split(':',1)[1].strip()
    def field(suffix):
        element=root.find(id='MainContent_'+suffix)
        if element is None:raise ValueError('Course field missing: '+suffix)
        return clean(element.get_text())
    description=field('lblDescription')
    expected,summary=REVIEWED[number]
    if hashlib.sha256(description.encode()).hexdigest()!=expected:
        raise ValueError('Course description changed; paraphrase needs review')
    raw=field('lblcredithours')
    if not re.fullmatch(r'\d+(?:\.\d+)?',raw):raise ValueError('Variable or unrecognized credit amount')
    c=course('usf','CAI '+number,name,'usf-ai-cai'+number,BASE+number,credits=float(raw),category='human_context' if number=='4024' else 'ai_ml')
    c['description']='2026–2027 public course inventory: '+summary
    values=[(label,field(suffix)) for label,suffix in [('Prerequisites','lblprereq'),('Corequisites','lblCorequisites'),('Co-prerequisites','lblcoprereq'),('Course restrictions','lblcreq'),('Other information','lblOtherInfo')]]
    c['prerequisites']='; '.join(label+': '+value for label,value in values if value) or None
    return dict(id=PID,courses=[c],notes=['Course inventory prerequisites preserve source Boolean choices, minimum grades, co-prerequisites and restrictions. Empty requisite fields stay unknown; they are not proof of no prerequisites. Published credit amounts have no verified normalized unit.'])

PARSERS={BASE+number:partial(parse_course,number=number) for number in REVIEWED}
