from importlib import import_module
from pathlib import Path
import pytest
m=import_module('atlas.adapters.mit-ai-decision-making-bs.hass_architecture')


def test_design_pdf_does_not_turn_studio_pair_into_arbitrary_choose_two():
    text='''Design HASS Concentration
Three subjects are required from two groups of study; two from Group 1 and one from Group 2.
Group 1: (two subjects)
4.021 Synthetic Studio (FA, 12 units, HASS-A) ~or~
4.02A Synthetic Intensive (IAP, 9 units, HASS-A)
~And~
4.053 Synthetic Required (FA, 12 units, HASS-A)
Group 2: (one subject)
4.999 Synthetic Elective (SP, 12 units, HASS-A)
'''
    d=m.parse_pdf_text('design',text)
    assert len(d['courses'])==4
    assert [r['kind'] for r in d['requirements'][1:]]==['choose_courses','all','choose_courses']
    assert [len(r['course_ids']) for r in d['requirements'][1:]]==[2,1,1]
    assert next(c for c in d['courses'] if c['code']=='4.02A')['credits']==9
    assert 'last_verified' not in d and 'curriculum_audit' not in d
    with pytest.raises(ValueError):m.parse_pdf_text('design',text.replace('~or~','~and~'))
    with pytest.raises(ValueError):m.parse_pdf_text('design',text.replace('4.053','4.054'))


def test_pdf_wrapped_rows_and_groups_are_source_observations():
    text='''History of Architecture, Art, and Design Concentration
Four subjects are required from two groups of study, three from Group 1 and one from Group 2
Group 1: History of Architecture and Design
• 4.999 Synthetic History (FA, HASS-A, 12
units)
History of Art
• 4.998 Synthetic Art (SP, HASS-A, 12 units)
Group 2: Art, Culture & Technology
Introductory Subjects
• 4.301 Synthetic Studio (SP, 12 units)
Intermediate / Advanced Subjects
• 4.314 Synthetic Wrapped
Course (FA, 12 units)
Total for Concentration in History of Architecture, Art, and Design = 4 subjects
'''
    d=m.parse_pdf_text('htc',text)
    assert len(d['courses'])==4
    assert d['courses'][-1]['name']=='Synthetic Wrapped Course'
    assert [r['count'] for r in d['requirements'][1:]]==[3,1]
    assert set(d['requirements'][1]['course_ids']).isdisjoint(d['requirements'][2]['course_ids'])
    with pytest.raises(ValueError):m.parse_pdf_text('htc',text.replace('12 units','variable units'))


@pytest.mark.parametrize('key',list(m.PDFS))
def test_optional_actual_architecture_pdf(key):
    p=Path('/tmp/atlas-mit-hass-rest-'+key+'.txt')
    if not p.exists():pytest.skip('Optional reviewed public PDF text')
    d=m.parse_pdf_text(key,p.read_text())
    assert d['courses'] and d['requirements']
    assert all(c['credits'] in [9,12] and c['credit_unit']=='units' for c in d['courses'])
    assert all('(FA' not in c['name'] and 'units)' not in c['name'] for c in d['courses'])


@pytest.mark.parametrize('key,fn',[('art-culture-and-technology',m.parse_act),('history-of-architecture-art-and-design',m.parse_htc),('architecture-undergraduate',m.parse_undergraduate)])
def test_optional_actual_architecture_html(key,fn):
    p=Path('/tmp/atlas-mit-hass-rest-'+key+'.html')
    if not p.exists():pytest.skip('Optional reviewed official HTML')
    d=fn(p.read_text());assert d['requirements'] and 'curriculum_status' not in d
    if key=='art-culture-and-technology':
        assert '404' in d['requirements'][-1]['summary']
        assert d['requirements'][-1]['course_ids']==[]


def test_optional_literature_info_sheet_scope():
    p=Path('/tmp/atlas-mit-hass-rest-literature-info.txt')
    if not p.exists():pytest.skip('Optional reviewed public PDF text')
    d=m.parse_literature_pdf_text(p.read_text())
    assert len(d['requirements'])==1 and d['requirements'][0]['kind']=='note'
    assert 'courses' not in d
