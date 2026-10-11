import pytest
from atlas.adapters.merced_public_context import parse_ai,parse_cse


def test_ai_context_distinguishes_aims_and_careers_without_inventing_curriculum():
    html='<main><h1>UC Merced Artificial Intelligence Program</h1><p>perceiving, reasoning, learning; algorithmic bias, data privacy; Artificial Intelligence is a new major, so there are no alumni yet; AI/Machine Learning Engineer; Data Scientist; Software Developer</p></main>'
    d=parse_ai(html)
    assert [o['statement_type'] for o in d['outcomes']]==['program_aim']*3+['career_pathway']
    assert not {'courses','requirements','first_offered','curriculum_status','last_verified'}&d.keys()
    with pytest.raises(ValueError):parse_ai(html.replace('no alumni yet','many alumni'))


def test_cse_outcomes_keep_host_degree_scope():
    html='<main><h1>Computer Science and Engineering Program Learning Outcomes</h1><p>Analyze a complex computing problem; Design, implement, and evaluate; Communicate effectively; legal and ethical principles; member or leader of a team; computer science theory and software development fundamentals</p></main>'
    d=parse_cse(html)
    assert len(d['outcomes'])==6 and all(o['text'].startswith('Host CSE program:') for o in d['outcomes'])
    assert all(o['statement_type']=='learning_outcome' for o in d['outcomes'])
    with pytest.raises(ValueError):parse_cse(html.replace('legal and ethical principles','new policy'))
    with pytest.raises(ValueError):parse_cse('<h1>Sign in</h1>'+html)
