"""Penn ARIN must not inherit unrelated CSCI elective quotas."""
import json
import pytest
from atlas.adapters.penn_bse.linked_policies import parse_technical_inventory,parse_technical_policy,faq_requirements
from bs4 import BeautifulSoup


def test_approved_conditional_and_rejected_entries_are_separated():
    data=[dict(course4d=f'TEST {1000+i}',title='Synthetic '+str(i),status=status,status_prefall24='yes') for i,status in enumerate(['restricted','unrestricted','ask','no'])]
    d=parse_technical_inventory(json.dumps(data))
    assert len(d['courses'])==3
    approved,conditional=d['requirements']
    assert approved['credits']==3 and len(approved['course_ids'])==2
    assert conditional['kind']=='note' and len(conditional['course_ids'])==1
    assert not set(approved['course_ids'])&set(conditional['course_ids'])
    assert all(c['credits'] is None for c in d['courses'])
    with pytest.raises(ValueError):parse_technical_inventory(json.dumps(data+[data[0]]))
    data[0]['status']='unknown'
    with pytest.raises(ValueError):parse_technical_inventory(json.dumps(data))


def test_arin_eligibility_is_guarded_and_csci_quota_is_not_inherited():
    html='<main><h1>Technical Electives</h1><p>ARIN degree: everything approved (i.e., yes/unrestricted/restricted) does count as a Technical Elective for these degrees as well; the rest of this article focuses solely on the 37CU CSCI Technical Electives.</p></main>'
    d=parse_technical_policy(html)
    assert len(d['requirements'])==1 and 'not applied here' in d['requirements'][0]['summary']
    with pytest.raises(ValueError):parse_technical_policy(html.replace('ARIN degree','NETS degree'))
    with pytest.raises(ValueError):parse_technical_policy(html.replace('solely','also'))
    with pytest.raises(ValueError):parse_technical_policy('<h1>Sign in</h1><input type="password">'+html)


def test_faq_changed_semester_limit_requires_review():
    html='Current Penn Engineering students, including current first- and second-year M&amp;T students. Submit a 4-year academic plan. Declare/Update Field of Study form. with the exception of CSCI, NETS and SSE. within 8 semesters in total (or 10 semesters for M&amp;T students). first day of their first-year Fall Semester.'
    assert len(faq_requirements(BeautifulSoup(html,'html.parser')))==4
    with pytest.raises(ValueError):faq_requirements(BeautifulSoup(html.replace('8 semesters','9 semesters'),'html.parser'))
