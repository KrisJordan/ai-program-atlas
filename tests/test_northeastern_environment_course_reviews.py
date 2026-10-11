import copy
import hashlib
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import northeastern_environment_course_reviews as m
from atlas.adapters.northeastern_courseleaf import clean


def block(code, name='Synthetic domain', text='Synthetic environmental methods.', hours=4, extra=''):
    return f'<div class="courseblock"><p class="courseblocktitle">{code}. {name}. ({hours} Hours)</p><p class="cb_desc">{text}</p>{extra}</div>'


def page(subject, content):
    return f'<div>2026-2027 Edition</div><div id="site-title"><h1>{m.SPEC["sources"][subject]["heading"]}</h1></div><div id="textcontainer">{content}</div>'


def install(monkeypatch, code, html):
    entry = copy.deepcopy(m.SPEC['courses'][code])
    entry['block_digest'] = hashlib.sha256(clean(BeautifulSoup(html, 'html.parser')).encode()).hexdigest()
    entry['description_guard'] = 'Synthetic environmental methods.'
    monkeypatch.setitem(m.SPEC['courses'], code, entry)
    return entry['targets'][0]['program_id']


def test_guarded_actual_observation_not_seed_review(monkeypatch):
    code = 'ENVR 1110'
    html = block(code, extra='<p class="courseblockextra">Prerequisite(s): A or B with C-</p><p class="courseblockextra">Corequisite(s): LAB 1000</p>')
    pid = install(monkeypatch, code, html)
    result = m.parse_subject(page('ENVR', html), program_id=pid, subject='ENVR', codes=[code])
    course = result['courses'][0]
    assert course['name'] == 'Synthetic domain'
    assert course['prerequisites'] == 'A or B with C-'
    assert course['credits'] == 4 and course['credit_unit'] == 'semester_hours'
    assert 'category_review' not in course
    assert result['requirements'] == []
    assert 'concurrent corequisite(s): LAB 1000' in result['notes'][0]
    for changed in [html.replace('methods.', 'changed.'), html.replace('4 Hours', '3 Hours'), html.replace('C-', 'B-'), html.replace('LAB 1000', 'LAB 2000'), html + html, '']:
        with pytest.raises(ValueError):
            m.parse_subject(page('ENVR', changed), program_id=pid, subject='ENVR', codes=[code])
    with pytest.raises(ValueError):
        m.parse_subject(page('ENVR', html).replace('2026-2027', '2025-2026'), program_id=pid, subject='ENVR', codes=[code])
    with pytest.raises(ValueError):
        m.parse_subject(page('ENVR', html), program_id='unreviewed-program', subject='ENVR', codes=[code])


def test_lab_depends_on_inspected_lecture_even_when_unselected(monkeypatch):
    lab, lecture = block('ENVR 2311', hours=1), block('ENVR 2310')
    pid = install(monkeypatch, 'ENVR 2311', lab)
    install(monkeypatch, 'ENVR 2310', lecture)
    result = m.parse_subject(page('ENVR', lab + lecture), program_id=pid, subject='ENVR', codes=['ENVR 2311'])
    assert len(result['courses']) == 1 and result['courses'][0]['credits'] == 1
    with pytest.raises(ValueError):
        m.parse_subject(page('ENVR', lab), program_id=pid, subject='ENVR', codes=['ENVR 2311'])


def test_manual_scope_and_dispositions():
    entries = m.SPEC['courses']
    assert len(entries) == 51
    assert sum(len(e['targets']) for e in entries.values()) == 69
    assert Counter(e['category'] for e in entries.values()) == {'applications': 40, 'other': 7, 'mathematics': 2, 'human_context': 2}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'} == {'ENVR 4970','ENVR 4971','ENVR 4997'}
    assert entries['EEMB 5130']['category'] == entries['ENVR 5500']['category'] == 'mathematics'
    assert 'may be taken concurrently' in entries['EEMB 5130']['prerequisites']
    assert entries['ENVR 5563']['prerequisites'].count('ENVR 5260') == 2
    assert entries['ENVR 1201']['corequisites'] is None
    assert 'may be taken concurrently' in entries['ENVR 1201']['prerequisites']


def test_optional_all_actual_catalog_blocks_and_idempotence():
    cache=Path('.cache/research/degree-audit-northeastern')
    if not all((cache/(s+'.html')).exists() for s in ('envr','eemb')):
        pytest.skip('Ignored actual-source caches are optional')
    groups = {}
    for code, entry in m.SPEC['courses'].items():
        for target in entry['targets']:
            groups.setdefault((target['program_id'], entry['subject']), []).append(code)
    observations = 0
    for (pid,subject), codes in groups.items():
        html=(cache/(subject.lower()+'.html')).read_text()
        a=m.parse_subject(html,program_id=pid,subject=subject,codes=codes)
        b=m.parse_subject(html,program_id=pid,subject=subject,codes=codes)
        assert a==b
        assert all('category_review' not in c for c in a['courses'])
        observations += len(a['courses'])
    assert observations == 69
