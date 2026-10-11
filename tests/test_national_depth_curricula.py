"""Local choices, conditional substitution, opaque IDs, and fresh observations."""
import hashlib
import json
from pathlib import Path
import pytest
from atlas import db
from atlas.adapters import national_depth_curricula as c
from atlas.adapters.national_depth_discovery import CONFIG

ROOT=Path(__file__).resolve().parents[1]
FSU='''<main><h1>(New) Artificial Intelligence Concentration</h1><div class="ai-concentration"><p>The CS@FSU Artificial Intelligence Concentration is designed for computer science students.</p><h3>Required Coursework</h3><ul>
<li>CAP 4601 — Intro AI</li><li>CAP 4613 — Deep Learning</li>
<li>CAP 4XXX — Agent Systems OR IDC 4290 — Data Projects</li>
<li>One of the following:<ul><li>COP 4870 — Full Stack</li><li>COP 4045 — Python</li><li>COP 4XXX — Systems Engineering</li><li>COP 4521 — Parallel Computing</li></ul></li>
<li>COP 4710 — Databases OR COP 4064 — Other Databases</li></ul></div></main>'''

def umass():
 def table(rows):return '<table><tr><td>Course</td><td>Title</td></tr>'+''.join(f'<tr><td>COMPSCI {code}</td><td>{title}</td></tr>' for code,title in rows)+'</table>'
 return '<main><h1>BS Artificial Intelligence Concentration Requirements</h1><p>The AI Concentration is available to students pursuing a BS in Computer Science.</p>'+table([('311','Algorithms'),('383','AI'),('389*','Introduction to Machine Learning')])+'<p>Students who qualify may substitute COMPSCI 589 Machine Learning for COMPSCI 389. Students may count both courses toward concentration requirements when applicable.</p><h2>AI Electives (Choose 2)</h2><p>At least one elective must be numbered 400 or above.</p>'+table([('348','Data Science'),('446 or 546','Search Engines / Applied Information Retrieval'),('589','Machine Learning')])+'</main>'


def smu(degree='BA',total=9,elective=3):
 if degree=='BA':
  section=f'<button aria-controls="ai">Artificial Intelligence and Machine Learning Track ({total} Credit Hours)</button><div id="ai">'
 else:
  section=f'<h2>Computer Science B.S. with a specialization in Artificial Intelligence and Machine Learning Specialization</h2><div>Requirements for the Specialization ({total} Credit Hours)'
 return f'<main><h1>CS-{degree} - Computer Science</h1>'+section+f'<p>Complete ALL of the following Courses: 0046401 0268171</p><p>{elective} credit hours of track electives approved by adviser</p></div><p>Total Credits 120</p><p>Technical electives cannot be satisfied by courses that are part of the student’s chosen track.</p></main>'


def test_fsu_preserves_placeholders_without_manufactured_courses():
 p=c.parse_fsu(FSU)
 assert len(p['courses'])==8
 assert not any('XXX' in x['code'] for x in p['courses'])
 assert len([r for r in p['requirements'] if 'placeholder' in r['id']])==2
 choices=[r for r in p['requirements'] if r['kind']=='alternative']
 assert len(choices)==2
 assert all(any(x['parent_id']==r['id'] and 'placeholder' in x['id'] for x in p['requirements']) for r in choices)
 database=next(r for r in p['requirements'] if r['id'].endswith('-database'))
 assert database['count']==1 and len(database['course_ids'])==2
 assert all(x['credits'] is None for x in p['courses'])


def test_fsu_changed_alternative_requires_review():
 with pytest.raises(ValueError):c.parse_fsu(FSU.replace(' OR ',' AND '))
 assert c.parse_fsu(FSU.replace('Intro AI','Revised Intro AI'))['courses'][0]['name']=='Revised Intro AI'


def test_umass_substitution_and_subset_do_not_add_requirements():
 p=c.parse_umass(umass());pid=CONFIG['umass'][0]
 core=next(r for r in p['requirements'] if r['id'].endswith('-ml-core'))
 assert core['count']==1 and core['course_ids']==[pid+'-compsci-389',pid+'-compsci-589']
 electives=next(r for r in p['requirements'] if r['id'].endswith('-electives'))
 subset=next(r for r in p['requirements'] if r['id'].endswith('-upper-level'))
 assert electives['count']==2 and subset['parent_id']==electives['id'] and subset['kind']=='note'
 assert len(p['courses'])==7
 assert {x['code'] for x in p['courses']} >= {'COMPSCI 446','COMPSCI 546'}
 assert not {'last_verified','curriculum_audit'} & p.keys()


def test_umass_requires_eligibility_and_substitution():
 with pytest.raises(ValueError):c.parse_umass(umass().replace('BS in Computer Science','MS in Computer Science'))
 with pytest.raises(ValueError):c.parse_umass(umass().replace('may substitute','may not substitute'))


@pytest.mark.parametrize('degree,key',[('BA','smu-ba'),('BS','smu-bs')])
def test_smu_never_fabricates_course_codes_from_publisher_ids(degree,key):
 p=c.parse_smu(smu(degree),key)
 assert {x['code'] for x in p['courses']} == {'CS 5320', 'CS 5324'}
 assert p['requirements'][1]['kind'] == 'all'
 unknown=c.parse_smu(smu(degree).replace('0268171','9999999'),key)
 assert len(unknown['courses']) == 1
 assert '9999999' in unknown['requirements'][-1]['summary']
 assert p['requirements'][0]['credits']==9
 assert p['requirements'][2]['credits']==3
 changed=c.parse_smu(smu(degree,total=12,elective=6),key)
 assert changed['requirements'][0]['credits']==12 and changed['requirements'][2]['credits']==6
 with pytest.raises(ValueError):c.parse_smu(smu('BA' if degree=='BS' else 'BS'),key)
 with pytest.raises(ValueError):c.parse_smu(smu(degree).replace('approved by adviser','chosen freely'),key)


def test_rpi_topics_are_not_a_complete_course_pool():
 p=c.parse_rpi('<main><h1>Cognitive Science of Artificial Intelligence, Minor</h1><p>Students must complete a minimum of 16 credits. Course topics may include: intelligent agents.</p></main>')
 assert not p['courses'] and p['requirements'][0]['credits']==16
 assert p['requirements'][0]['kind']=='note' and p['requirements'][0]['credit_unit']=='unknown'


@pytest.mark.parametrize('key,fn,html', [('fsu',c.parse_fsu,FSU),('umass',c.parse_umass,umass()),('smu-ba',lambda h:c.parse_smu(h,'smu-ba'),smu())])
def test_access_and_navigation_guards(key,fn,html):
 with pytest.raises(ValueError):fn('<h1>Access denied</h1>'+html)
 with pytest.raises(ValueError):fn('<nav>'+html+'</nav><main><h1>Unrelated</h1></main>')


def test_pdf_prerequisite_blocks_are_observed_not_seed_replay():
 text='Computer Science Concentration in AI\nThis Concentration requires 15 Credits:\n'
 for i in range(8):text+=f'CAP {4601+i} (3)\nExample {i}\n*Prerequisite - COP {3300+i}*\n'
 p=c.parse_fsu_flowchart_text(text)
 assert len(p['courses'])==8 and p['courses'][0]['prerequisites']=='COP 3300'
 assert p['requirements'][0]['credits']==15
 assert all(x['credit_unit']=='unknown' for x in p['courses'])
 changed=c.parse_fsu_flowchart_text(text.replace('requires 15','requires 18').replace('COP 3300','COP 3399'))
 assert changed['requirements'][0]['credits']==18 and changed['courses'][0]['prerequisites']=='COP 3399'
 with pytest.raises(ValueError):c.parse_fsu_flowchart_text(text.replace('Computer Science Concentration in AI','Other program'))


@pytest.mark.parametrize('key',['fsu','umass','rpi','smu-ba','smu-bs'])
def test_curated_partial_scope_and_provenance(key):
 p=json.loads((ROOT/'data/programs'/(CONFIG[key][0]+'.json')).read_text());db.validate_program(p)
 assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
 assert p['curriculum_audit']['scope']==p['program_kind']
 assert p['requirements'] and p['first_offered'] is None


@pytest.mark.parametrize('url,fn',[(c.UMASS_BS,c.parse_umass_bs),(c.UMASS_TRANSFER,c.parse_umass_transfer),(c.SMU_CREDIT,lambda h:c.parse_smu_credit(h,'smu-ba'))])
def test_optional_actual_policy_replays(url,fn):
 path=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
 if not path.exists():pytest.skip('Optional source cache absent')
 p=fn(path.read_text());assert p['requirements'];assert not {'curriculum_audit','last_verified','curriculum_status'} & p.keys()
 with pytest.raises(ValueError):fn('<h1>Access denied</h1>'+path.read_text())


@pytest.mark.parametrize('publisher_id',c.SMU_COURSES)
def test_optional_smu_course_metadata(publisher_id):
 url=c.SMU_COURSE_URLS[publisher_id];path=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
 if not path.exists():pytest.skip('Optional source cache absent')
 data=c.parse_smu_course(path.read_text(),'smu-ba',publisher_id)['courses'][0]
 assert data['credits']==3 and data['credit_unit']=='semester_hours'
 assert data['prerequisites'].startswith('C- or better') and data['description']
 with pytest.raises(ValueError):c.parse_smu_course(path.read_text().replace('Undergraduate','Graduate'),'smu-ba',publisher_id)
