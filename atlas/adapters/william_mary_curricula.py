"""William & Mary department observations; catalog completeness is reviewed separately."""
import re
from atlas.adapters.national_curriculum_common import clean, content, course, rule, require_phrases

BASE='https://cdsp.wm.edu/'
DS=BASE+'data-science/degrees/bs_minor/'
BA=BASE+'data-science/degrees/ba_appliedai/'


def identity(pid, title, kind):
    return dict(id=pid,title=title,program_kind=kind,award_level='BA' if kind=='degree' else kind)


def declaration(html,pid,applied=False):
    heading='Declaring a Major in Applied AI' if applied else 'Declaring a Major in Data Science'
    root=content(html,heading)
    require_phrases(root,['minimum of 39 and maximum of 54 credit hours','including AP, IB, and other transfer credits','advisor','University Registrar'])
    sid=pid+'-declaration'
    groups=[rule(pid+'-declare', 'Major declaration and advising', sid,kind='note',summary='Declare after 39–54 earned credit hours, including AP, IB and transfer credit. Request an advisor, review the major declaration with the advisor, and submit the signed form to the Registrar. Annual advisor check-ins are recommended.')]
    result={'id':pid,'requirements':groups}
    if applied:return result
    require_phrases(root,['the three elective courses'])
    rows=[row for row in [r for t in root.find_all('table') for r in t.find_all('tr')] if row.find('td') and clean(row.find('td').get_text())=='Artificial Intelligence']
    if len(rows)!=1:raise ValueError('AI specialization row absent or ambiguous')
    cells=rows[0].find_all('td',recursive=False)
    if len(cells)!=2:raise ValueError('AI specialization table structure changed')
    rowtext=clean(cells[1].get_text(' ',strip=True))
    if 'Course options:' not in rowtext:raise ValueError('AI course options absent')
    options=rowtext.split('Course options:',1)[1]
    matches=re.findall(r'(DATA\s+\d{3})\s*\(([^)]+)\)',options)
    if not matches or len(matches)!=len(re.findall(r'DATA\s+\d{3}',options)):raise ValueError('Unrecognized course option syntax')
    courses=[course('wm-ds-ai',clean(code),name,sid,DS+'declare-bsdsci/',category='ai_ml') for code,name in matches]
    groups.insert(0,rule(pid+'-electives','Choose three AI specialization courses',sid,[c['id'] for c in courses],kind='choose_courses',count=3,category='ai_ml',summary='Choose three elective courses from the Artificial Intelligence specialization row. DATA 440 is listed as Special Topics; this department page does not specify eligible topics.'))
    result.update(courses=courses,outcomes=[dict(text='Develop or apply AI algorithms to large data sets.',kind='source_stated',source_id=sid,locator='Artificial Intelligence specialization row')])
    return result


def department_policies(root,pid,applied=False):
    sid=pid+'-identity'
    require_phrases(root,['syllabus of the course you took','voted on by our curriculum committee','no more than one page','The desired number of credits (3 or 4)','must receive pre-approval','The Capstone requirement must be satisfied at W&M','nearly equivalent to a W&M Data Science course','DATA 340 (Special Topics)','after consulting with the Data Science Curriculum Committee'])
    specs=[('substitution','Transfer, AP and cross-department substitutions','Substitutions require departmental review of the prior course and syllabus; curriculum committee approval may be required.'),('research','External-faculty independent research','For DATA 490 with a faculty member outside Data Science, the faculty member submits a proposal of no more than one page describing goals, data, methods and the desired 3 or 4 credits. Curriculum committee approval is required.'),('abroad','Study abroad and residency','Study-abroad credit requires departmental preapproval. The listed core courses should be taken at W&M, with rare exceptions requiring curriculum committee consent; the capstone must be completed at W&M.'),('equivalency','Study-abroad equivalency','Equivalent approved courses transfer under the corresponding W&M course number after faculty review. Relevant courses without a W&M equivalent may transfer as DATA 340 after faculty and curriculum committee review.'),('eligibility','Arts & Sciences declaration','Students already in Arts & Sciences may declare directly without a separate application to the School of Computing, Data Sciences & Physics.')]
    require_phrases(root,['already students in Arts & Sciences at William & Mary','do not need to apply separately' if not applied else 'to not need to apply separately'])
    return [rule(pid+'-'+key,title,sid,kind='note',summary=summary) for key,title,summary in specs]


def ds_overview(html):
    pid='william-mary-data-science-ai-specialization'
    root=content(html,'Bachelors of Science & Minor in Data Science')
    require_phrases(root,['Choose one track','Artificial Intelligence','36-credit program'])
    result=identity(pid,'Artificial Intelligence','concentration')
    groups=department_policies(root,pid)
    require_phrases(root,['DATA 201 Intro to Data Science','DATA 202 Ethics in Data Science','DATA 301 Applied Machine Learning','DATA 302 Databases','DATA 303 Data Visualization'])
    groups.append(rule(pid+'-host-scope','Host major context',pid+'-identity',kind='note',summary='This is one specialization in the 36-credit Data Science BS. Shared major core and university degree requirements are outside the local specialization inventory. The department identifies DATA 201, 202, 301, 302 and 303 as core courses normally taken at W&M.'))
    result['requirements']=groups
    return result


def ba_overview(html):
    pid='william-mary-applied-ai-ba';sid=pid+'-identity'
    root=content(html,'Major in Applied AI')
    require_phrases(root,['BA in Interdisciplinary Studies with a Major in Applied Artificial Intelligence','30-credit undergraduate major','DATA 201 Intro to Data Science','DATA 202 Ethics in Data Science','DATA 305 Designing AI Agents'])
    text=clean(root.get_text(' ',strip=True));match=re.search(r'The core requirements below should be taken at W&M, including (.+?)\. Exceptions',text)
    if not match:raise ValueError('Core residency list absent')
    entries=re.findall(r'(DATA \d{3})\s+(.+?)(?=,\s*(?:and\s+)?DATA|$)',match[1])
    if len(entries)!=3:raise ValueError('Unrecognized core residency list')
    courses=[course('wm-applied-ai',code,name.strip(' ,'),sid,BA,category='human_context' if code=='DATA 202' else 'other') for code,name in entries]
    groups=[rule(pid+'-major-credits','Major credit minimum',sid,kind='note',credits=30,summary='The department describes a 30-credit undergraduate major. This is the major total, not the complete BA degree total.'),rule(pid+'-observed-core','Core courses named in residency policy',sid,[c['id'] for c in courses],summary='The FAQ explicitly names these core courses. This is an incomplete inventory; DATA 305 conflicts with AAI 301 in the linked example pathway.')]+department_policies(root,pid,True)
    require_phrases(root,['choose the right AI tools','coordinating multiple tools/agents','portfolio of real deliverables'])
    result=identity(pid,'Applied Artificial Intelligence','degree')
    result.update(courses=courses,requirements=groups,outcomes=[dict(text='Frame open-ended problems, select AI tools, evaluate outputs, coordinate AI agents and communicate results. Build a portfolio demonstrating responsible professional AI use.',kind='source_stated',source_id=sid,locator="What You'll Gain")])
    return result


def ai_minor(html):
    pid='william-mary-ai-minor';sid=pid+'-identity'
    root=content(html,'Minoring in Artificial Intelligence')
    text=clean(root.get_text(' ',strip=True))
    match=re.search(r'minor in Artificial Intelligence requires (\d+) credits',text)
    require_phrases(root,['open to students from all majors','machine learning, data analysis, and responsible AI use','ethics and societal impact'])
    if not match:raise ValueError('Minor credit total absent')
    result=identity(pid,'Artificial Intelligence','minor')
    result.update(requirements=[rule(pid+'-credits','Minor credit minimum',sid,kind='note',credits=int(match[1]),summary='The department publishes this credit minimum; the detailed catalog course list is not accessible.'),rule(pid+'-eligibility','Open to all majors',sid,kind='note',summary='Students in any major may pursue the AI minor.')],outcomes=[dict(text='Combine machine learning, data analysis and responsible AI with attention to ethics, societal effects and interdisciplinary applications.',kind='source_stated',source_id=sid,locator='Program overview')])
    return result


def cs_concentration(html):
    pid='william-mary-cs-ai-ml-concentration';sid=pid+'-identity'
    root=content(html,'Bachelor of Science (B.S.) in Computer Science')
    require_phrases(root,['When declaring their major, students pursuing the B.S. in Computer Science must select a concentration','Artificial Intelligence/Machine Learning','Each concentration features a distinct set of required courses and electives'])
    result=identity(pid,'Artificial Intelligence/Machine Learning','concentration')
    result['requirements']=[rule(pid+'-declaration','Choose the concentration when declaring the major',sid,kind='note',summary='CS BS students select a concentration when declaring the major. AI/Machine Learning has its own required and elective courses; those courses are not enumerated on this department page.')]
    return result
