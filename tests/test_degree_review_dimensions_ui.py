from bs4 import BeautifulSoup
from atlas.site import degree_audit_program


def test_partial_dimensions_never_inherit_full_or_neighbor_certification():
    html = degree_audit_program({'program_kind': 'degree', 'degree_audit': {'status': 'audited', 'second_pass_status': 'verified', 'core_review': {'reviewed_at': '2026-10-11', 'reviewer': 'Reader', 'dimensions': {'fixed_requirements': {'status': 'verified', 'summary': 'Bounded fixed set.', 'evidence': [], 'limitations': []}}}}})
    page = BeautifulSoup(html, 'html.parser')
    assert [x.get_text() for x in page.select('.review-dimension-status')] == ['Verified within stated scope', 'Not independently reviewed', 'Not independently reviewed']
    assert 'Whole-degree correctness audit: Audited' in page.get_text()
    assert degree_audit_program({'program_kind': 'minor'}) == ''


def test_dimension_prose_is_escaped_and_evidence_urls_are_safe():
    html = degree_audit_program({'program_kind': 'degree', 'degree_audit': {'status': 'blocked', 'core_review': {'reviewer': '<script>bad()</script>', 'dimensions': {'classification': {'status': 'unverified', 'summary': '<img src=x>', 'evidence': [{'url': 'javascript:bad()', 'locator': '<b>source</b>'}], 'limitations': ['<script>bad()</script>']}}}}})
    assert '<script>bad()' not in html and '<img src=x>' not in html
    assert 'href="javascript:' not in html
    assert '&lt;b&gt;source&lt;/b&gt;' in html
    assert '&lt;script&gt;bad()&lt;/script&gt;' in html
