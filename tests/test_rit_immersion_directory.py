import json
from pathlib import Path
import pytest
from atlas.adapters.rit_immersion_directory import parse, TITLE


def fixture(body):
    return f'<main><h1>{TITLE}</h1>{body}</main>'


def test_directory_observes_exact_links_without_inventing_rules():
    html = fixture('<a href="/study/example-immersion">Example Immersion</a>'
                   '<a href="/study/example-minor">Example Minor</a>'
                   '<a href="https://example.org/study/false-immersion">False Immersion</a>')
    assert parse(html) == {'observed_routes': [{'id': 'example-immersion', 'title': 'Example Immersion', 'url': 'https://www.rit.edu/study/example-immersion'}]}


def test_rejects_shell_login_and_navigation_only_identity():
    for html in [fixture(''), '<nav><h1>'+TITLE+'</h1></nav>', fixture('<input type="password"><a href="/study/a-immersion">A Immersion</a>')]:
        with pytest.raises(ValueError): parse(html)


def test_queue_keeps_unknown_course_total_and_all_published_routes():
    q = json.loads(Path('research/rit-immersion-route-queue.json').read_text())
    assert len(q['routes']) == len({r['url'] for r in q['routes']}) == 77
    assert q['queue_totals']['total_distinct_route_courses'] is None
    assert q['status'] == 'in_progress'
    for route in q['routes']:
        if route['status'] == 'identity_reviewed_rules_unread':
            assert route['rules'] is None and route['course_codes'] is None
    assert q['university_rule']['closed_universe'] is False


def test_all_routes_have_rules_but_named_content_queue_is_not_full_completion():
    q=json.loads(Path('research/rit-immersion-route-queue.json').read_text())
    work=json.loads(Path('research/rit-immersion-course-review-queue.json').read_text())
    assert q['queue_totals']['routes_with_reviewed_rules']==77
    assert q['queue_totals']['routes_with_unread_rules']==0
    assert all(r['rules'] is not None for r in q['routes'])
    assert sum(len(r['course_codes']) for r in q['routes'])==1324
    union={c for r in q['routes'] for c in r['course_codes']}
    assert len(union)==787
    assert union=={c['code'] for c in work['courses']}
    assert work['review_state_counts']=={'pending_actual_course_content':195,'existing_reviewed_description':547,'historical_reference_only':3,'reviewed_contribution_not_integrated':42}
    assert len([c for c in work['courses'] if c['assigned_reviewer']=='root_languages'])==107
    assert len(work['open_routes'])==1 and work['open_routes'][0]['id']=='global-experience-immersion'
    assert q['queue_totals']['total_distinct_route_courses'] is None
    assert q['status']==work['status']=='in_progress'
    assert 'PRFL/WGST-330' in union and not any('category_review' in c for c in work['courses'])
