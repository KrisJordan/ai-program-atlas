"""Rendered Stevens AI requirement panels; open eligibility rules stay open."""
import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, course, rule, require_phrases

PID='stevens-institute-of-technology-artificial-intelligence-bs-degree'
URL='https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv/requirements-and-concentrations-n90Np'
SID=PID+'-rules'
CODE=r'[A-Z]+ \d+(?: / [A-Z]+ \d+)?'


def parse(html):
    soup=BeautifulSoup(html,'html.parser')
    if not soup.find(lambda n:n.name=='h1' and clean(n.get_text())=='Bachelor of Science in Artificial Intelligence'):
        raise ValueError('Expected catalog BS heading')
    if any(clean(a.get_text())=='course' for a in soup.find_all('a',attrs={'data-course-id':True})):
        raise ValueError('Unhydrated course references; browser rendering required')
    courses={};rules=[]
    def panel(title):
        button=soup.find(lambda n:n.name=='button' and clean(n.get_text())==title)
        p=soup.find(id=button.get('aria-controls')) if button else None
        if p is None:raise ValueError('Missing rendered requirement panel: '+title)
        return p
    def labels(node):
        out=[clean(a.get_text()) for a in node.find_all('a',attrs={'data-course-id':True})]
        if any(not re.fullmatch(CODE,c) for c in out):raise ValueError('Unhydrated or malformed course reference')
        return out
    def ids(codes):
        result=[]
        for code in codes:
            c=course('stevens',code,None,SID,URL)
            courses[c['id']]=c;result.append(c['id'])
        return result
    def add(suffix,title,kind='note',codes=(),**kw):
        r=rule(PID+'-'+suffix,title,SID,ids(codes),kind=kind,**kw);rules.append(r);return r['id']
    ms=panel('Math/Science Requirements')
    require_phrases(ms,['two science courses and a science laboratory'])
    table=ms.find('table')
    if table is None:raise ValueError('Science sequence table missing')
    parent=add('science-sequences','Science sequences','alternative',summary='Select one published sequence of two science courses and one laboratory; the chemistry/biology row permits a lab alternative.')
    rows=table.find('tbody').find_all('tr',recursive=False) if table.find('tbody') else table.find_all('tr')[1:]
    if not rows:raise ValueError('Empty science sequence table')
    for i,row in enumerate(rows,1):
        cells=row.find_all('td',recursive=False)
        if len(cells)<4 or any(clean(c.get_text()) for c in cells[4:]):raise ValueError('Science table structure changed')
        name=clean(cells[0].get_text());lectures=labels(cells[1])+labels(cells[2]);labs=labels(cells[3])
        if len(lectures)!=2 or len(labs) not in (1,2):raise ValueError('Science row choice changed')
        seq=add('science-sequence-'+str(i),name,'all',lectures+(labs if len(labs)==1 else []),parent=parent,summary='Complete this row only if this science sequence is selected.')
        if len(labs)==2:
            require_phrases(cells[3],['or'])
            add('science-sequence-'+str(i)+'-lab','Laboratory alternative','alternative',labs,parent=seq,summary='Choose one lab within this selected sequence.')
    math=panel('Math/Science Electives')
    require_phrases(math,['complete two Math/Science electives','Any 3-credit Physics (PEP), Chemistry (CH), Biology (BIO) or Mathematics (MA) course','required course in the degree program','equivalent to another course counted towards the degree','prior approval','following courses may also count'])
    value=clean(math.get_text(' ',strip=True));excluded=re.findall(r'MA \d+',value)
    extras=labels(math)
    add('math-science-electives','Math/science electives','choose_courses',count=2,summary='Choose two 3-credit PEP, CH, BIO or MA courses, or the separately named additional options, with prior academic-advisor approval. Required and equivalent coursework is excluded. Published examples of excluded equivalents: '+', '.join(excluded)+'. This is an open eligibility rule, not an incomplete finite list.')
    add('math-science-extra-options','Additional math/science options','note',extras,summary='These named courses may also satisfy the open math/science-elective rule; they are not the entire eligible pool.')
    tech=panel('Technical Electives');require_phrases(tech,['prior approval','from the following list'])
    m=re.search(r'complete (\d+) Technical electives',clean(tech.get_text(' ',strip=True)))
    if not m:raise ValueError('Technical elective count missing')
    options=labels(tech)
    if len(options)!=len(set(options)) or not options:raise ValueError('Duplicate or empty technical options')
    add('technical-electives','Technical electives','choose_courses',options,count=int(m[1]),summary='Choose the specified number from the published finite pool, with prior academic-advisor approval. A cross-listed label is one option; undergraduate graduate-course access rules also apply.')
    gen=panel('General Electives');require_phrases(gen,['Any 3+-credit course offered at Stevens','required course in the degree program','equivalent to another course counted towards the degree','prior approval'])
    m=re.search(r'complete (\d+) General Electives',clean(gen.get_text(' ',strip=True)))
    if not m:raise ValueError('General elective count missing')
    add('general-electives','General electives','choose_courses',count=int(m[1]),summary='Choose the specified number of Stevens courses carrying at least three credits, with prior academic-advisor approval. Required/equivalent courses and the separately recorded exclusions cannot count. This published open route requires no invented finite course pool.')
    restrictions=gen.find(lambda n:n.name=='p' and clean(n.get_text()).startswith('The following courses cannot be counted'))
    pairs=gen.find(lambda n:n.name=='p' and clean(n.get_text()).startswith('Also, students may not count toward the major both courses'))
    if restrictions is None or pairs is None:raise ValueError('General exclusion or overlap section missing')
    excluded=labels(restrictions);paircodes=labels(pairs)
    if not excluded or not paircodes or len(paircodes)%2:raise ValueError('Malformed exclusion/overlap list')
    # These codes restrict eligibility; they are not added as eligible course records.
    add('general-exclusions','General-elective exclusions',summary='Excluded courses: '+', '.join(excluded)+'.')
    add('overlap-pairs','Pairs that cannot both count',summary='Do not count both courses in any pair: '+'; '.join(a+' with '+b for a,b in zip(paircodes[::2],paircodes[1::2]))+'. Cross-listed labels remain one member of a pair.')
    success=panel('SUCCESS Curriculum Requirements');paragraphs=success.find_all('p')
    req=next((p for p in paragraphs if clean(p.get_text()).startswith('All students must complete')),None)
    choice=next((p for p in paragraphs if clean(p.get_text()).startswith('Students must complete three courses from')),None)
    if req is None or choice is None:raise ValueError('SUCCESS structure missing')
    required=labels(req);options=labels(choice)
    if not required or len(options)<3:raise ValueError('SUCCESS options missing')
    add('success-required','SUCCESS first-year requirement','all',required,summary='Complete the named first-year requirement, subject to the separately published Clark Scholars substitution.')
    add('success-choice','SUCCESS Frontiers choice','choose_courses',options,count=3,summary='Choose three of the published Frontiers courses.')
    human=panel('Humanities Requirements')
    link=human.find('a',href=True)
    if link is None or clean(link.get_text())!='Humanities Requirements':raise ValueError('Humanities policy reference missing')
    add('humanities-policy','Humanities policy reference',summary='Apply the linked university Humanities Requirements, including the AI-specific School of Computing row recorded separately; the program plan and policy describe the same allocations rather than duplicate requirements.')
    return dict(id=PID,curriculum_status='partial',courses=list(courses.values()),requirements=rules)
