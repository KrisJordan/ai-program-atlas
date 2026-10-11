"""Observe current IU specialization requirements and their directly applicable policies."""
import re
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases

PROGRAM_ID='indiana-cs-ai-specialization'
BASE='https://bulletins.iu.edu/iub/sice/2026-2027/undergraduate/'
SOURCES=(BASE+'degree-programs/bs-computer-science/artificial-intelligence.shtml',BASE+'degree-programs/bs-computer-science/specializations.shtml',BASE+'degree-programs/bs-computer-science/luddy-degree-major-req.shtml',BASE+'courses/computer-science.shtml')
SID=PROGRAM_ID+'-requirements'
PATTERN=r'(CSCI-[A-Z] \d{3}|MATH-M \d{3}|STAT-S \d{3})\s+(.+)'


def parse(html):
    root=content(html,'Artificial Intelligence Specialization')
    if root.find_parent(['nav','aside','footer']):raise ValueError('Navigation is not specialization evidence')
    section=root.find(id='image_hd_content')
    if not section or not section.find('h5',string='Artificial Intelligence Specialization'):raise ValueError('IU AI specialization heading missing')
    outer=section.find('ol');items=outer.find_all('li',recursive=False) if outer else []
    if len(items)!=3:raise ValueError('IU specialization selection structure changed')
    courses={};groups=[]
    for index,(li,count) in enumerate(zip(items,[2,2,1]),1):
        header=clean(' '.join(str(x) for x in li.contents if isinstance(x,str)))
        expected='Select '+('two' if count==2 else 'one')+' course'
        if not header.startswith(expected) or (index==2 and 'if not used above' not in header):raise ValueError('IU course selection rule changed')
        gid=f'iu-ai-selection-{index}'
        groups.append(rule(gid,f'Selection {index}: choose {count}',SID,kind='choose_courses',count=count,summary=f'Choose {count} listed course option'+('s' if count>1 else '')+'.'+(' Do not reuse courses from the first selection.' if index==2 else '')))
        options=li.find('ul')
        if not options:raise ValueError('IU selection course list missing')
        for n,entry in enumerate(options.find_all('li',recursive=False),1):
            text=clean(entry.get_text(' ',strip=True));parts=re.split(r'\s+OR\s+',text);ids=[]
            for part in parts:
                match=re.fullmatch(PATTERN,part)
                if not match:raise ValueError('Unrecognized IU course option')
                code,name=match.groups();topic=name if '(Topic:' in name else None
                c=course('iu-ai',code,name,SID,SOURCES[0],category='ai_ml' if index<3 else 'foundations',topic=topic)
                courses[c['id']]=c;ids.append(c['id'])
            groups.append(rule(f'{gid}-option-{n}',' or '.join(parts),SID,ids,parent=gid,kind='choose_courses' if len(ids)>1 else 'all',count=1 if len(ids)>1 else None))
    return dict(id=PROGRAM_ID,title='Computer Science — Artificial Intelligence specialization',award_level='concentration',program_kind='concentration',catalog_year='2026-2027',courses=list(courses.values()),requirements=groups)


def parse_specialization_policies(html):
    root=content(html,'Specializations')
    require_phrases(root,['Equivalent honors versions of regular courses may substitute for all requirements','add or change your specialization through SAMS','minimum grade of C- in each specialization course','Artificial Intelligence'])
    sid=PROGRAM_ID+'-specialization-policies'
    return dict(id=PROGRAM_ID,requirements=[rule('iu-ai-honors','Honors equivalents',sid,kind='note',summary='Equivalent honors versions can replace regular courses in the specialization.'),rule('iu-ai-declaration','Declaration and minimum grade',sid,kind='note',summary='Add or change the specialization through SAMS. Earn at least C-minus in every specialization course.')])


def parse_major_policies(html):
    root=content(html,'Luddy Degree and Major Requirements')
    require_phrases(root,['choose a specialization area before their junior year','If used in specialization area (excluding the Security specialization), it may not be used to satisfy this requirement','Courses may not double count between this requirement, Mathematical Science Requirement, Major Requirements, or specialization area requirements'])
    sid=PROGRAM_ID+'-current-bulletin'
    return dict(id=PROGRAM_ID,requirements=[rule('iu-ai-advising','Specialization planning',sid,kind='note',summary='Choose a specialization before the junior year in consultation with an academic advisor.'),rule('iu-ai-overlap','Restrictions on overlapping requirements',sid,kind='note',summary='AI specialization courses cannot also satisfy the mathematical-science requirement. Natural-science requirement courses cannot double count toward specialization, mathematical science or major requirements. The host CS major and degree retain their separate requirements.')])


def parse_course_metadata(html):
    root=content(html,'Computer Science');sid=PROGRAM_ID+'-cs-courses'
    wanted={'CSCI-B '+n for n in ['351','355','363','365','401','403','405','455','456','457','490']}|{'CSCI-P 415'}
    result=[]
    for item in root.find_all('li',class_='nobullet'):
        h=item.find(class_='ctitle')
        if not h:continue
        m=re.fullmatch(r'(CSCI-[A-Z] \d{3}) (.+) \((\d+(?:\.\d+)?(?:-\d+)?) cr\.\)',clean(h.get_text(' ',strip=True)))
        if not m or m[1] not in wanted:continue
        code,name,amount=m.groups();topic=None
        if code=='CSCI-B 490':
            name+=' (Topic: Generative AI and Applications)';topic=name
        c=course('iu-ai',code,name,sid,SOURCES[3],credits=None if '-' in amount else float(amount),topic=topic,category='foundations' if code in {'CSCI-B 401','CSCI-B 403','CSCI-B 405','CSCI-P 415'} else 'ai_ml')
        remaining=clean(item.get_text(' ',strip=True))[len(clean(h.get_text(' ',strip=True))):].strip()
        prerequisite=re.match(r'P:\s*(.+?\.)\s',remaining)
        if prerequisite:c['prerequisites']=prerequisite[1]
        result.append(c)
    if len(result)!=12:raise ValueError('Expected IU CS course metadata missing')
    return dict(id=PROGRAM_ID,courses=result)

SOURCE_PARSERS={SOURCES[0]:parse,SOURCES[1]:parse_specialization_policies,SOURCES[2]:parse_major_policies,SOURCES[3]:parse_course_metadata}


# Bounded metadata review: observations do not certify a curriculum audit.
from functools import partial as _metadata_partial
from atlas.adapters.small_complete_metadata_batch2 import CONFIG as _metadata_config, parse_metadata as _parse_metadata

SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
for _key in ['indiana-cs-ai-specialization-source-4']:
    _cfg = _metadata_config[_key]
    if _cfg["url"] not in SOURCES:
        SOURCES = list(SOURCES) + [_cfg["url"]]
    SOURCE_PARSERS[_cfg["url"]] = _metadata_partial(_parse_metadata, key=_key)
