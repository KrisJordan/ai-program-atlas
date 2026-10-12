from copy import deepcopy
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.requirement_context import related_option_groups
from atlas.site import requirement_tree


def test_real_mit_five_groups_use_current_source_routes_without_reparenting():
    p=json.loads((Path(__file__).resolve().parents[1]/'data/programs/mit-ai-decision-making-bs.json').read_text());before=deepcopy(p)
    groups=related_option_groups(p['requirements'])['mit-ai-v2025-centers']
    assert [g['title'].split()[0] for g in groups]==['Data-centric','Model-centric','Decision-centric','Computation-centric','Human-centric']
    soup=BeautifulSoup(requirement_tree(p),'html.parser');section=soup.select_one('[data-related-pool=mit-ai-v2025-centers]')
    assert [len(x.select(':scope > .related-option-routes > li')) for x in section.select('.related-course-group')]==[4,5,3,4,7]
    assert section.parent.get('class') == ['requirement-body']
    assert len(section.select('.related-course-group')) == 5
    assert not any(n.has_attr('open') for n in section.select('.related-course-group'))
    assert soup.select_one('#requirement-mit-ai-v2025-centers-1 .requirement-course-name')
    assert len(soup.select('.requirement'))==len(p['requirements'])
    assert p==before


def test_shared_components_are_not_complete_routes_and_other_sources_do_not_match():
    r=lambda id,kind,parent,cids=(),source='s':dict(id=id,kind=kind,parent_id=parent,course_ids=list(cids),source_id=source,title=id)
    graph=[r('pool','choose_courses','root'),r('bundle','all','pool',['a','b']),r('single','all','pool',['c']),r('partial','note','root'),r('part','all','partial',['a']),r('different-source','note','root',source='other'),r('same-route','all','different-source',['a','b'],source='other'),r('exact','note','root'),r('exact-route','all','exact',['b','a'])]
    assert [g['id'] for g in related_option_groups(graph)['pool']]==['exact']
