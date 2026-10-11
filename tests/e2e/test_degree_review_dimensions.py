"""Bounded core judgments must not inherit whole-degree policy blockers."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from playwright.sync_api import expect

from atlas.site import build
from tests.test_site import site_data  # noqa: F401
from tests.e2e.test_atlas import browser  # noqa: F401

pytestmark = pytest.mark.e2e


@pytest.fixture
def dimension_site(tmp_path, site_data):
    # Presentation fixture, not a substitute for Rice's primary source audit.
    rice = site_data['programs'][0]
    rice.update(title='Rice AI review fixture', institution={**rice['institution'], 'name': 'Rice University'})
    evidence = {'url': 'https://ga.rice.edu/programs-study/departments-programs/engineering-computing/computer-science/artificial-intelligence-bsai/', 'locator': 'Required courses: COMP 140, COMP 182 and COMP 215'}
    rice['degree_audit'] = {
        'status': 'blocked', 'second_pass_status': 'partial',
        'core_review': {'reviewed_at': '2026-10-11', 'reviewer': 'Independent source reviewer', 'dimensions': {
            'fixed_requirements': {'status': 'verified', 'summary': 'The 13 mapped fixed identities include three computing foundations courses.', 'evidence': [evidence], 'limitations': ['Summer and fall/spring residency wording remains unresolved.']},
            'choice_rules': {'status': 'partial', 'summary': 'Printed option rules were checked; one policy interaction remains open.', 'evidence': [evidence], 'limitations': ['No student-specific pathway has been selected.']},
            'classification': {'status': 'verified', 'summary': 'The required chart includes three computing foundations and two systems courses.', 'evidence': [evidence], 'limitations': ['A bounded chart review does not certify every degree policy.']},
        }},
    }
    other = site_data['programs'][1]
    other.update(program_kind='degree', award_level='BA', degree_audit={'status': 'in_progress'})
    site_data['meta']['degree_audit'] = dict(scope_programs=2, audited=0, blocked=1, in_progress=1, pending=0, second_pass_verified=0, audit_date='2026-10-11', programs=[rice['degree_audit'], other['degree_audit']])
    build(site_data, tmp_path/'ai-program-atlas')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/ai-program-atlas/'
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize('width', [1440, 390])
def test_blocked_degree_preserves_verified_core_and_keyboard_evidence(browser, dimension_site, width):
    context = browser.new_context(viewport={'width': width, 'height': 1000})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(dimension_site+'programs/test-ai-0/')
        panel = page.locator('.degree-audit-program')
        expect(panel.get_by_role('heading', name='Whole-degree correctness audit: Blocked')).to_be_visible()
        expect(panel).to_contain_text('Whole-degree independent second pass: Partial')
        expect(panel).to_contain_text('2026-10-11')
        expect(panel).to_contain_text('Independent source reviewer')
        fixed = panel.locator('[data-review-dimension="fixed_requirements"]')
        expect(fixed.locator('.review-dimension-status')).to_have_text('Verified within stated scope')
        expect(fixed).to_contain_text('three computing foundations courses')
        expect(panel.locator('[data-review-dimension="choice_rules"] .review-dimension-status')).to_have_text('Partially reviewed')
        expect(panel.locator('[data-review-dimension="classification"]')).to_contain_text('three computing foundations and two systems')
        summary = fixed.locator('summary')
        summary.focus()
        page.keyboard.press('Enter')
        expect(fixed.locator('details')).to_have_attribute('open', '')
        expect(fixed).to_contain_text('residency wording remains unresolved')
        expect(fixed.get_by_role('link')).to_have_attribute('href', 'https://ga.rice.edu/programs-study/departments-programs/engineering-computing/computer-science/artificial-intelligence-bsai/')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('label[for="profile-options"]').click()
        expect(page.locator('#profile-options')).to_be_checked()
        expect(fixed.locator('.review-dimension-status')).to_have_text('Verified within stated scope')
        page.reload()
        expect(panel.get_by_role('heading', name='Whole-degree correctness audit: Blocked')).to_be_visible()
        expect(fixed.locator('.review-dimension-status')).to_have_text('Verified within stated scope')
        page.goto(dimension_site+'programs/test-ai-1/')
        expect(page.locator('.review-dimension-status')).to_have_text(['Not independently reviewed']*3)
        for route in ['coverage/', 'methodology/']:
            page.goto(dimension_site+route)
            expect(page.locator('.degree-audit-summary')).to_contain_text('These counts describe whole-degree reviews')
            expect(page.locator('.degree-audit-summary')).to_contain_text('an unresolved policy does not erase a verified curriculum correction')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert errors == []
    finally:
        context.close()
