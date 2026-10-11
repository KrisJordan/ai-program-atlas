"""Disjoint MIT HASS contribution: source identities and withheld decisions matter."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'atlas/adapters/mit-ai-decision-making-bs'
SPEC = importlib.util.spec_from_file_location('mit_hass_review', ADAPTER / 'reviewed_hass_subjects.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)
MANIFEST = json.loads((ADAPTER / 'reviewed_hass_subjects.json').read_text())
SEED = json.loads((ROOT / 'data/programs/mit-ai-decision-making-bs.json').read_text())


def entry(code):
    return next(r for r in MANIFEST['courses'].values() if r['listed_code'] == code)


def test_scope_is_exact_and_unread_records_are_not_certified():
    hass = {c['id'] for c in SEED['courses'] if c['id'].startswith('mit-ai-hass-')}
    assert set(MANIFEST['courses']) == hass
    assert len(hass) == 845
    assert MANIFEST['full_audit_status'] == 'partial'
    for row in MANIFEST['courses'].values():
        if row['review_status'] == 'pending':
            assert row['observations'] == []
        for evidence in row['observations']:
            if evidence.get('evidence_basis') == 'official_title_only':
                assert evidence['description_digest'] is None
                assert evidence['description_summary'] is None
                if evidence['prerequisites'] is not None:
                    assert evidence['source_id']=='mit-ai-hass-review-economics-titles'
                    assert evidence['prerequisites'] in evidence['source_metadata']['source_annotation']
                if evidence['credits'] is not None:
                    assert evidence['units_text']=='9 unit IAP version' and evidence['credits']==9
                assert 'title' in evidence['rationale']
            elif evidence.get('evidence_basis') == 'official_code_only':
                assert evidence['observed_name'] is evidence['description_digest'] is evidence['description_summary'] is None
                assert evidence['credits'] is evidence['prerequisites'] is None
                assert evidence['status']=='unclassified' and evidence['category']=='other'
            else:
                assert evidence['description_digest']
                assert evidence['description_summary']
            assert evidence['source_id'] in MANIFEST['source_specs']


def test_probability_literature_is_not_math_and_music_is_not_automatic_ai():
    assert entry('21L.017')['observations'][0]['category'] == 'human_context'
    music = entry('21M.080')['observations'][0]
    assert music['category'] == 'applications'
    assert music['credits'] == 12
    assert music['unit_rule_source_url'] == 'https://catalog.mit.edu/subjects/'


def test_half_term_subjects_preserve_hass_bundle_and_permission():
    greek = entry('21L.608')['observations'][0]
    assert greek['credits'] == 6
    assert greek['prerequisites'] == '21L.607 or permission of instructor'
    assert any('oneHASS-H' in text for text in greek['restrictions'])
    assert entry('21L.614')['observations'][0]['credits'] == 6


def test_graduate_prerequisite_not_transferred_to_undergraduate():
    observation = entry('4.603')['observations'][0]
    assert observation['prerequisites'] is None
    assert observation['observed_prerequisite_field'] == '4.604: permission of instructor'
    assert any('graduate4.604 only' in text for text in observation['restrictions'])


def test_conflicting_and_changed_identity_evidence_is_withheld():
    for row in MANIFEST['courses'].values():
        if row['review_status'] in {'identity_review_needed', 'source_conflict'}:
            assert not any(o['approved_for_integration'] for o in row['observations'])
    writing = [r for r in MANIFEST['courses'].values() if any(o['observed_code'] == 'WGS.231' for o in r['observations'])]
    assert writing and all(r['review_status'] == 'source_conflict' for r in writing)


def test_review_reuse_is_guarded_by_source_context_and_entire_observation():
    obs = dict(code='21L.017', name='The Art of the Probable', description='Literary history.', term='Fall 2026', prerequisites='none')
    course = dict(id='test', code='21L.017', name='The Art of the Probable', source_id='listed-source')
    evidence = dict(approved_for_integration=True, source_url='https://lit.mit.edu/example', observation_digest=review.observation_digest(obs))
    manifest = {'courses': {'test': dict(listed_code=course['code'], listed_name=course['name'], listed_source_id=course['source_id'], review_status='reviewed', observations=[evidence])}}
    assert review.matched_review(course, obs, evidence['source_url'], manifest) == evidence
    for field in ['description', 'name', 'term', 'prerequisites']:
        changed = copy.deepcopy(obs); changed[field] = 'changed'
        assert review.matched_review(course, changed, evidence['source_url'], manifest) is None
    assert review.matched_review(course, obs, 'https://example.org/other', manifest) is None
    assert review.matched_review({**course, 'source_id': 'another-version'}, obs, evidence['source_url'], manifest) is None


def test_triplets_need_actual_notation_rule_and_unknown_remains_null():
    html = '<p>The total unit credit for a subject is obtained by adding together all the units shown.</p>'
    assert review.unit_total('3-0-3; second half of term', html) == 6
    assert review.unit_total('0-0-0', html) == 0
    assert review.unit_total('Units arranged', html) is None
    with pytest.raises(ValueError, match='convention'):
        review.unit_total('3-0-9', html.replace('adding', 'averaging'))


@pytest.mark.parametrize('key,parser', [('architecture',review.observe_architecture), ('literature',review.observe_literature), ('music-schedule',review.observe_performing_arts), ('theater-schedule',review.observe_performing_arts)])
def test_actual_source_cache_reviews_reproduce_when_cache_available(key, parser):
    path = Path('/tmp/mit-hass-subjects') / (key + '.html')
    if not path.exists():
        pytest.skip('Optional ignored official source capture')
    observations = parser(path.read_text())
    source_specs = {s['url'] for s in MANIFEST['source_specs'].values() if s.get('parser') in {'architecture','literature','performing_arts'}}
    matched = []
    for course in SEED['courses']:
        for obs in observations:
            for url in source_specs:
                hit = review.matched_review(course, obs, url, MANIFEST)
                if hit:matched.append(hit)
    assert matched
    assert all(hit['approved_for_integration'] for hit in matched)


def test_cmsw_visible_term_parser_keeps_alias_and_meeting_distinct():
    html = '''<section id="mit-subject-list"><h2>Fall 2026</h2>
    <li class="academic_term_tier__subject">
    <a class="academic_term_tier__subject-course-number">CMS.611[J]</a>
    <span class="academic_term_tier__subject-course-title">Creating Video Games</span>
    <div class="academic-term-tier__subject-description"><ul>
    <li><strong>Same subject as:</strong> 6.4570[J]</li>
    <li><strong>Meets with:</strong> CMS.900</li><li><strong>Units:</strong> 3-3-6</li>
    </ul><p>Teams combine game programming and art production.</p></div></li></section>'''
    row = review.observe_cmsw(html)[0]
    assert row['term'] == 'Fall 2026'
    assert row['same_subject_as'] == '6.4570[J]'
    assert row['meets_with'] == 'CMS.900'
    assert row['prerequisites'] is None
    assert row['description'] == 'Teams combine game programming and art production.'
    with pytest.raises(ValueError, match='term label'):
        review.observe_cmsw(html.replace('Fall 2026', 'Unknown'))
    with pytest.raises(ValueError, match='paired'):
        review.observe_cmsw(html.replace('academic-term-tier__subject-description', 'changed'))


def test_cmsw_manual_subject_and_identity_judgments():
    observations = [o for r in MANIFEST['courses'].values() for o in r['observations']
                    if o['source_id'] == 'mit-ai-hass-review-cmsw-fall2026']
    by_code = {o['observed_code']: o for o in observations}
    assert by_code['CMS.401']['category'] == 'human_context'
    assert by_code['CMS.611[J]']['status'] == 'mixed'
    assert by_code['CMS.611[J]']['candidate_categories'] == ['foundations', 'applications']
    assert by_code['CMS.591[J]']['prerequisites'] == 'Permission of instructor. Coreq: CMS.586'
    assert by_code['CMS.357[J]']['prerequisites'] is None
    assert by_code['CMS.357[J]']['credits'] == 12
    malformed = [r for r in MANIFEST['courses'].values() if '.WGS.' in r['listed_code']]
    assert malformed and all(r['review_status'] == 'identity_review_needed' for r in malformed)


def test_cmsw_actual_visible_capture_replays_approved_observations():
    path = Path('/tmp/mit-hass-subjects/cmsw-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public visible-DOM capture')
    rows = review.observe_cmsw(path.read_text())
    hashes = {review.observation_digest(row) for row in rows}
    observations = [o for r in MANIFEST['courses'].values() for o in r['observations']
                    if o['source_id'] == 'mit-ai-hass-review-cmsw-fall2026']
    assert len(observations) == 35
    assert all(o['observation_digest'] in hashes for o in observations)


def test_cmsw_archived_term_credits_and_missing_description_are_not_imputed():
    rows=[r for r in MANIFEST['courses'].values() if any(o['source_id']=='mit-ai-hass-review-cmsw-spring2026' for o in r['observations'])]
    obs={o['observed_code']:o for r in rows for o in r['observations'] if o['source_id']=='mit-ai-hass-review-cmsw-spring2026'}
    assert obs['CMS.305[J]']['credits']==9
    assert obs['CMS.C35[J]']['credits']==15
    assert obs['CMS.C35[J]']['status']=='mixed'
    assert obs['CMS.702']['category']=='human_context'
    assert obs['CMS.593[J]']['prerequisites']=='CMS.592'
    assert all(o['catalog_year']=='Spring 2026' for o in obs.values())
    hamilton=[r for r in MANIFEST['courses'].values() if r['listed_code'].startswith('CMS.427')]
    assert hamilton and all(r['observations'][0]['evidence_basis']=='official_title_only' for r in hamilton)
    assert all(not any(o['source_id']=='mit-ai-hass-review-cmsw-spring2026' for o in r['observations']) for r in hamilton)
    assert all(r['observations'][-1]['source_id']=='mit-ai-hass-review-literature-aliases-spring2026' for r in hamilton)
    changed=next(r for r in rows if r['listed_name']=='Intersectionality, Neurodiversity, and Disability')
    assert changed['review_status']=='identity_review_needed'


def test_cmsw_spring_visible_capture_replays_without_assuming_latest_term():
    path=Path('/tmp/mit-hass-subjects/cmsw-spring2026-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public archived-term capture')
    source=review.observe_cmsw(path.read_text())
    assert {o['term'] for o in source}=={'Spring 2026'}
    assert next(o for o in source if o['code']=='CMS.427[J]')['description'] is None
    hashes={review.observation_digest(o) for o in source}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-cmsw-spring2026']
    assert len(saved)==32 and all(o['observation_digest'] in hashes for o in saved)


def test_cmsw_2025_interactive_writing_does_not_force_a_programming_path():
    records=[r for r in MANIFEST['courses'].values() if any(o['source_id']=='mit-ai-hass-review-cmsw-fall2025' for o in r['observations'])]
    obs={o['observed_code']:o for r in records for o in r['observations'] if o['source_id']=='mit-ai-hass-review-cmsw-fall2025'}
    assert obs['CMS.618[J]']['category']=='human_context'
    assert any('OR structuring text' in x for x in obs['CMS.618[J]']['restrictions'])
    assert obs['CMS.560']['category']=='human_context'
    assert obs['CMS.560']['prerequisites'] is None
    changed=[r for r in MANIFEST['courses'].values() if r['listed_code']=='CMS.400']
    assert changed and all(r['review_status']=='identity_review_needed' for r in changed)


@pytest.mark.parametrize('term',['fall2025','spring2025'])
def test_cmsw_2025_visible_capture_replays_exact_dated_observations(term):
    path=Path('/tmp/mit-hass-subjects')/f'cmsw-{term}-visible.html'
    if not path.exists():
        pytest.skip('Optional ignored public archived-term capture')
    hashes={review.observation_digest(o) for o in review.observe_cmsw(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-cmsw-{term}']
    assert saved and all(o['observation_digest'] in hashes for o in saved)


def test_official_language_title_reviews_do_not_invent_description_or_identity():
    assert MANIFEST['evidence_counts']['description_reviewed_records']==314
    assert MANIFEST['evidence_counts']['title_only_reviewed_records']>=45
    for code in ['21G.715','21G.111','21H.186']:
        o=entry(code)['observations'][-1]
        assert o['evidence_basis']=='official_title_only'
        assert o['status']=='unclassified' and o['category']=='other'
        assert o['description_summary'] is o['description_digest'] is o['credits'] is None
    assert entry('21G.901')['observations'][-1]['category']=='human_context'
    for code in ['21G.094','21G.612','21G.613','21G.614']:
        assert entry(code)['review_status']=='identity_review_needed'
        assert not entry(code)['observations'][-1]['approved_for_integration']


@pytest.mark.parametrize('language',['french','spanish','chinese','japanese','korean','portuguese','russian'])
def test_actual_language_schedule_title_observations_replay(language):
    path=Path('/tmp')/f'atlas-mit-hass-rest-{language}.html'
    if not path.exists():
        pytest.skip('Optional ignored official language page capture')
    observations=review.observe_language_titles(path.read_text())
    hashes={review.observation_digest(o) for o in observations}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-language-titles-{language}']
    assert saved and all(o['observation_digest'] in hashes for o in saved)
    assert all(o['description'] is o['prerequisites'] is o['units'] is None for o in observations)


def test_language_observer_uses_printed_code_not_a_conflicting_link():
    html='''<main><h1>French &amp; Francophone Studies</h1><div class="value">Fall 2026</div>
    <div><div class="credit-section-wrap"><div class="value">21G</div>
    <div class="semester-section-titile"><div class="value">333</div></div>
    <a href="https://example.edu/#21G.304">catalog link</a></div>
    <div><div class="value">French IV</div></div></div></main>'''
    o=review.observe_language_titles(html)[0]
    assert o['code']=='21G.333' and o['name']=='French IV'
    assert o['linked_urls']==['https://example.edu/#21G.304']
    assert o['description'] is None
    with pytest.raises(ValueError,match='identity/term'):
        review.observe_language_titles(html.replace('Fall 2026','Term unknown'))


def test_political_pool_membership_does_not_classify_computing_or_methods():
    rows=[r for r in MANIFEST['courses'].values() if r['listed_source_id']=='mit-ai-decision-making-bs-hass-political-subfields']
    bycode={r['listed_code']:r for r in rows}
    for code in ['17.835','17.C08J','17.811','17.447J','17.803']:
        o=bycode[code]['observations'][-1]
        assert o['category']=='other' and o['status']=='unclassified'
        assert o['evidence_basis']=='official_title_only'
        assert o['description_digest'] is None
    assert bycode['17.055']['observations'][-1]['category']=='human_context'
    assert bycode['17.567']['observations'][-1]['credits']==9
    assert 'Washington Summer Internship' in bycode['17.307']['observations'][-1]['restrictions'][0]
    assert 'current IAP offering' in bycode['17.567']['observations'][-1]['restrictions'][0]


def test_actual_political_pdf_title_review_replays_with_source_guards():
    path=Path('/tmp/atlas-mit-political-subfields.txt')
    if not path.exists():
        pytest.skip('Optional ignored official PDF extraction')
    text=path.read_text();rows=review.observe_political_pdf_titles(text)
    hashes={review.observation_digest(o) for o in rows}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-political-pdf-titles']
    assert len(rows)==66 and len(saved)==65
    assert all(o['observation_digest'] in hashes for o in saved)
    with pytest.raises(ValueError,match='Unrecognized PDF line'):
        review.observe_political_pdf_titles(text.replace('Models and Methods','Changed heading'))


def test_sts_titles_preserve_unknowns_and_actual_crosslisted_content():
    o=entry('STS.024')['observations'][-1]
    assert o['observed_code']=='CMS.524[J]' and o['status']=='mixed'
    assert o['category']=='other' and o['source_metadata']['same_subject_as']=='STS.024[J]'
    assert entry('STS.081J')['observations'][-1]['status']=='unclassified'
    assert entry('STS.085J')['observations'][-1]['category']=='human_context'
    old=next(r for r in MANIFEST['courses'].values() if r['listed_name']=='Quantifying People: A History of Social Science')
    assert old['review_status']=='identity_review_needed'
    assert not old['observations'][-1]['approved_for_integration']


def test_sts_title_parser_has_source_shape_guard_and_no_category_guess():
    html='<h1>Tier II Subjects</h1><p><a href="https://example.edu/STS053">STS.053 Multidisciplinary Interactive Learning Through Problem-Solving</a></p>'
    o=review.observe_sts_titles(html)[0]
    assert o['code']=='STS.053' and o['description'] is None
    assert 'category' not in o and o['prerequisites'] is None
    with pytest.raises(ValueError,match='heading'):
        review.observe_sts_titles(html.replace('Tier II Subjects','New title'))


@pytest.mark.parametrize('tier',['i','ii'])
def test_sts_actual_source_title_review_replays(tier):
    path=Path('/tmp')/f'atlas-mit-hass-rest-sts-tier-{tier}.html'
    if not path.exists():
        pytest.skip('Optional ignored official STS title page')
    hashes={review.observation_digest(o) for o in review.observe_sts_titles(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-sts-tier-{tier}-titles']
    assert saved and all(o['observation_digest'] in hashes for o in saved)


def test_anthropology_renamed_identity_and_broad_titles_are_not_silently_classified():
    old=entry('21A.503/ 24.913/ STS.070')
    assert old['review_status']=='identity_review_needed'
    assert old['observations'][-1]['observed_name']=='The Human Past: Introduction to Archaeology'
    assert not old['observations'][-1]['approved_for_integration']
    for code in ['21A.511','21A.157','21A.406J']:
        o=next(o for o in entry(code)['observations'] if o.get('evidence_basis')=='official_title_only')
        assert o['category']=='other' and o['status']=='unclassified'
        assert o['description_digest'] is None
    assert entry('21A.504J')['observations'][-1]['category']=='human_context'
    grad=entry('21A.409J/11.238J')['observations'][-1]
    assert any('graduate (G)' in text for text in grad['restrictions'])
    sound=entry('21A.505')['observations'][-1]
    assert sound['observed_code']=='CMS.406[J]' and sound['description_digest']
    assert '21A.505[J]' in sound['source_metadata']['same_subject_as']


def test_anthropology_title_parser_keeps_meeting_and_level_evidence_without_inference():
    html='''<h1>MIT Anthropology Subjects</h1><table class="subjects-table"><tr>
    <td>21A.550J/ STS.064J (meets with 21A.559)</td><td><a href="https://example.edu/catalog">DV Lab (U/G)</a></td></tr></table>'''
    row=review.observe_anthropology_titles(html)[0]
    assert row['code']=='21A.550J' and 'meets with 21A.559' in row['course_label']
    assert row['name']=='DV Lab (U/G)' and row['description'] is None
    assert 'category' not in row
    with pytest.raises(ValueError,match='heading'):
        review.observe_anthropology_titles(html.replace('MIT Anthropology Subjects','Subjects changed'))


def test_anthropology_actual_directory_replays_title_observations():
    path=Path('/tmp/mit-hass-subjects/anthropology-subjects.html')
    if not path.exists():
        pytest.skip('Optional ignored official Anthropology directory capture')
    hashes={review.observation_digest(o) for o in review.observe_anthropology_titles(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-anthropology-titles']
    assert len(saved)==32 and all(o['observation_digest'] in hashes for o in saved)


def test_economic_pool_does_not_certify_mathematics_computing_or_current_offering():
    for code in ['14.12','14.15[J]','14.17','14.18','14.78[J]']:
        row=next(o for o in entry(code)['observations'] if o['source_id']=='mit-ai-hass-review-economics-titles')
        assert row['category']=='other' and row['status']=='unclassified'
        assert row['description_digest'] is None
    assert entry('14.70')['observations'][-1]['category']=='human_context'
    assert entry('14.27')['observations'][-1]['prerequisites']=='14.30 or 6.041'
    assert next(o for o in entry('14.16')['observations'] if o['source_id']=='mit-ai-hass-review-economics-titles')['prerequisites']=='14.03/14.04'
    assert entry('14.01')['observations'][-1]['prerequisites'] is None
    assert any('not offered in2026–27' in x for x in entry('14.73')['observations'][-1]['restrictions'])


def test_actual_economics_concentration_observer_preserves_source_context():
    path=Path('/tmp/atlas-mit-hass-economics.html')
    if not path.exists():
        pytest.skip('Optional ignored official Economics concentration capture')
    text=path.read_text();rows=review.observe_economics_titles(text)
    assert len(rows)==34
    # Adjacent minor's statistics, finance bundle and AI title are not concentration entries.
    assert not {'14.30','15.401/417','14.C395'} & {o['code'] for o in rows}
    hashes={review.observation_digest(o) for o in rows}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-economics-titles']
    assert len(saved)==37 and all(o['observation_digest'] in hashes for o in saved)
    with pytest.raises(ValueError):
        review.observe_economics_titles(text.replace('One or two of:','One or three of:'))


def test_history_title_reviews_do_not_classify_broad_titles_from_department():
    for code in ['21H.228','21H.284','21H.321J [11.026]','21H.388']:
        o=entry(code)['observations'][-1]
        assert o['category']=='other' and o['status']=='unclassified'
    for code in ['21H.165','21H.319','21H.333','21H.244J [21G.085]']:
        o=next(o for o in entry(code)['observations'] if o.get('evidence_basis')=='official_title_only')
        assert o['category']=='human_context' and o['evidence_basis']=='official_title_only'
        assert o['description_summary'] is None
    # Prior substantively changed versions are not overwritten by a later old-list title review.
    assert entry('21H.151')['review_status']=='identity_review_needed'


def test_actual_shass_title_review_replays_all_nine_fields_and_rejects_policy_change():
    source_specs=[(sid,s) for sid,s in MANIFEST['source_specs'].items() if s.get('parser')=='shass_field_titles']
    assert len(source_specs)==10
    matched=0
    for sid,spec in source_specs:
        path=Path('/tmp')/('atlas-mit-hass-'+spec['field_key']+'.html')
        if not path.exists():
            pytest.skip('Optional ignored SHASS field capture')
        rows=review.observe_shass_field_titles(spec['field_key'],path.read_text())
        assert all('category' not in row and row['description'] is None for row in rows)
        hashes={review.observation_digest(o) for o in rows}
        saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==sid]
        assert saved and all(o['observation_digest'] in hashes for o in saved)
        matched+=len(saved)
    assert matched==229
    text=Path('/tmp/atlas-mit-hass-american-studies.html').read_text()
    with pytest.raises(ValueError):
        review.observe_shass_field_titles('american-studies',text.replace('taking four subjects','taking five subjects'))


def test_remaining_field_title_snapshot_keeps_performance_and_science_unknown():
    for code in ['21M.226','21M.291','3.985J [5.24J]','3.987','21G.067','21L.590']:
        o=next(o for r in MANIFEST['courses'].values() if r['listed_code']==code for o in r['observations'] if o['source_id'].startswith('mit-ai-hass-review-field-titles-'))
        assert o['status']=='unclassified' and o['category']=='other'
        assert o['description_digest'] is None
    for code in ['21G.705','21L.001','STS.085J/6.805J','17.571','WGS.226J [STS.023]']:
        o=next(o for o in entry(code)['observations'] if o['source_id'].startswith('mit-ai-hass-review-field-titles-'))
        assert o['category']=='human_context'
        assert o['evidence_basis']=='official_title_only'
    # Foundations in a literature/policy title does not establish programming content.
    assert entry('21L.001')['observations'][-1]['observed_name']=='Foundations of Western Literature: Homer to Dante'
    assert MANIFEST['full_audit_status']=='partial'


def test_final_named_lists_keep_technical_and_variable_subjects_unknown():
    for code in ['24.S00','11.074','11.154','9.00','CMS.603','MAS.110']:
        o=entry(code)['observations'][-1]
        assert o['status']=='unclassified' and o['category']=='other'
        assert o['description_digest'] is None
    for code in ['24.C40J/6.C40J','24.901','11.148','11.013[J]']:
        o=entry(code)['observations'][-1]
        assert o['category']=='human_context'
    for code in ['STS.021J/WGS160J','STS.022J21A.407J/21G.057J/WGS.275J','17035J/21H.181J']:
        r=entry(code)
        assert r['review_status']=='identity_review_needed'
        assert not r['observations'][-1]['approved_for_integration']


@pytest.mark.parametrize('kind,file',[
    ('computing','atlas-mit-hass-computing.html'),('ethics','atlas-mit-hass-philosophy.html'),
    ('linguistics','atlas-mit-hass-rest-linguistics.html'),('urban','atlas-mit-hass-rest-urban-studies.html'),
    ('education','atlas-mit-cmsw-browser-projection-education.html'),('cms_pool','atlas-mit-cmsw-browser-projection-pool.html')])
def test_remaining_list_title_observations_replay_exact_public_source(kind,file):
    path=Path('/tmp')/file
    if not path.exists():
        pytest.skip('Optional ignored public source capture')
    rows=review.observe_remaining_list_titles(kind,path.read_text())
    assert all('category' not in r and r['description'] is None for r in rows)
    hashes={review.observation_digest(o) for o in rows}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-list-titles-'+kind]
    assert saved and all(o['observation_digest'] in hashes for o in saved)
    changed=copy.deepcopy(rows[0]);changed['name']='Unseen changed subject'
    assert review.observation_digest(changed) not in {o['observation_digest'] for o in saved}


def test_non_delegated_hass_scope_has_explicit_dispositions_without_full_audit_claim():
    pending={cid for cid,r in MANIFEST['courses'].items() if r['review_status']=='pending'}
    architecture=json.loads((ADAPTER/'reviewed_architecture_remainder.json').read_text())
    # The other primary contribution retains ownership of exactly these source records.
    assert len(pending)==58
    assert all(MANIFEST['courses'][cid]['listed_code'].startswith('4.') for cid in pending)
    assert MANIFEST['counts']==dict(scope=845,reviewed=765,identity_review_needed=20,source_conflict=2,pending=58)
    assert sum(MANIFEST['evidence_counts'].values())==765
    assert MANIFEST['full_audit_status']=='partial'
    assert pending == set(architecture['courses'])


def test_code_only_unknowns_do_not_invent_titles_or_content():
    for code in ['21G.342','21G.347','21M.223J']:
        o=entry(code)['observations'][-1]
        assert o['evidence_basis']=='official_code_only'
        assert o['observed_name'] is o['description_summary'] is o['credits'] is None
        assert o['status']=='unclassified' and o['category']=='other'
        assert o['approved_for_integration']
    for code in ['21G.312','21G.346']:
        o=entry(code)['observations'][-1]
        assert o['evidence_basis']=='official_description' and o['description_digest']
        assert o['catalog_year']=='Spring 2027' and o['category']=='human_context'
        assert o['prerequisites'] is o['credits'] is None


def test_french_spotlight_parser_binds_description_and_term_and_not_schedule_title():
    html='''<main><h1>French &amp; Francophone Studies</h1><div class="value">Spring 2027</div>
    <div class="value"><p><strong>21G.312 Oceanic Writing</strong></p><p>Close reading in French.</p>
    <p><strong>A note regarding the enrollment policy:</strong> limited to18.</p></div></main>'''
    o=review.observe_french_spotlights(html)[0]
    assert o['code']=='21G.312' and o['description']=='Close reading in French.'
    assert o['term']=='Spring 2027' and 'limited to18' in o['enrollment']
    assert o['units'] is o['prerequisites'] is None
    with pytest.raises(ValueError,match='description missing'):
        review.observe_french_spotlights(html.replace('<p>Close reading in French.</p>',''))
    with pytest.raises(ValueError,match='term missing'):
        review.observe_french_spotlights(html.replace('Spring 2027','Unknown term'))


def test_actual_final_code_and_description_observations_replay():
    sources=[('french-spotlights','atlas-mit-hass-rest-french.html',review.observe_french_spotlights),
             ('code-only-language_placement','atlas-mit-hass-rest-language-placement.html',lambda text:review.observe_remaining_list_titles('language_placement',text)),
             ('code-only-music','atlas-mit-hass-music-degree.html',lambda text:review.observe_remaining_list_titles('music',text))]
    for source,file,parser in sources:
        path=Path('/tmp')/file
        if not path.exists():
            pytest.skip('Optional ignored official source capture')
        hashes={review.observation_digest(o) for o in parser(path.read_text())}
        saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-'+source]
        assert saved and all(o['observation_digest'] in hashes for o in saved)


def test_literature_description_upgrades_preserve_half_term_bundle_and_dated_topics():
    latin1=entry('21L.611')['observations'][-1];latin2=entry('21L.612')['observations'][-1]
    assert latin1['credits']==latin2['credits']==6
    assert latin1['prerequisites']=='none' and latin2['prerequisites']=='21L.611 or permission of instructor'
    assert all(any('petition after both' in r for r in o['restrictions']) for o in [latin1,latin2])
    assert latin1['catalog_year']==latin2['catalog_year']=='Spring 2026'
    style=entry('21L.504J [WGS.140]')['observations'][-1]
    assert style['category']=='human_context' and style['prerequisites']=='Permission of instructor'
    assert style['observed_name'].endswith('Style in an Age of Sameness')
    assert style['description_digest'] and style['evidence_basis']=='official_description'
    spanish=entry('21L.636J [21G.716]')['observations'][-1]
    assert spanish['catalog_year']=='Fall 2026'
    assert spanish['prerequisites']=='One intermediate subject in Spanish or permission of instructor'


def test_actual_literature_spring_description_upgrade_replays_and_changed_prerequisite_withdraws():
    path=Path('/tmp/mit-hass-subjects/literature-spring2026-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored expanded public Literature archive capture')
    rows=review.observe_literature(path.read_text());byhash={review.observation_digest(o):o for o in rows}
    saved=[(cid,r,o) for cid,r in MANIFEST['courses'].items() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-literature-spring2026']
    assert len(saved)==8
    for cid,r,e in saved:
        o=byhash[e['observation_digest']]
        assert o['description'] and o['term']=='Spring 2026'
        course=dict(id=cid,code=r['listed_code'],name=r['listed_name'],source_id=r['listed_source_id'])
        assert review.matched_review(course,o,e['source_url'],MANIFEST)==e
        changed={**o,'prerequisites':'New prerequisite'}
        assert review.matched_review(course,changed,e['source_url'],MANIFEST) is None


def test_literature_other_topic_is_not_transferred_to_specific_ai_topic():
    rows=[r for r in MANIFEST['courses'].values() if r['listed_code']=='21L.707']
    ai=next(r for r in rows if 'AI and' in r['listed_name'])
    generic=next(r for r in rows if r['listed_name']=='Problems in Cultural Interpretation')
    assert ai['observations'][0]['evidence_basis']=='official_title_only'
    assert ai['observations'][-1]['observed_name']==ai['listed_name']
    assert ai['observations'][-1]['catalog_year']=='Spring 2025'
    assert ai['observations'][-1]['category']=='human_context'
    assert ai['observations'][-1]['prerequisites']=='Two subjects in Literature or permission of instructor'
    assert generic['observations'][-1]['observed_name'].endswith('The Art of War and Peace')
    assert generic['observations'][-1]['catalog_year']=='Fall 2025'
    narrative=entry('21L.489[J]')['observations'][-1]
    assert narrative['category']=='human_context' and narrative['prerequisites']=='none'
    assert any('programming or text-structuring alternatives' in r for r in narrative['restrictions'])


def test_actual_literature_fall2025_upgrade_and_public_heading_only_boundary():
    path=Path('/tmp/mit-hass-subjects/literature-fall2025-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public Literature archive')
    rows=review.observe_literature(path.read_text());hashes={review.observation_digest(o) for o in rows}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-literature-fall2025']
    assert len(saved)==6 and all(o['observation_digest'] in hashes for o in saved)
    checks=[r for r in MANIFEST['source_checks'] if r.get('status')=='public_heading_only']
    assert {r['url'] for r in checks}>={'https://canvas.mit.edu/courses/39868','https://canvas.mit.edu/courses/39662','https://canvas.mit.edu/courses/39654'}
    assert all('not proof of authentication-only' in r['reason'] for r in checks)


def test_spring2025_literature_exact_topic_and_changed_text_guard():
    sid='mit-ai-hass-review-literature-spring2025'
    saved=[(cid,r,o) for cid,r in MANIFEST['courses'].items() for o in r['observations'] if o['source_id']==sid]
    assert len(saved)==3
    assert all(o['category']=='human_context' and o['credits']==12 for _,_,o in saved)
    path=Path('/tmp/mit-hass-subjects/literature-spring2025-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored expanded public Literature archive')
    byhash={review.observation_digest(o):o for o in review.observe_literature(path.read_text())}
    for cid,r,e in saved:
        o=byhash[e['observation_digest']]
        course=dict(id=cid,code=r['listed_code'],name=r['listed_name'],source_id=r['listed_source_id'])
        assert review.matched_review(course,o,e['source_url'],MANIFEST)==e
        assert review.matched_review(course,{**o,'description':'Different topic with a changed description'},e['source_url'],MANIFEST) is None


def test_literature_cancelled_offering_keeps_description_without_availability_claim():
    novel=entry('21L.501')['observations'][-1]
    assert novel['observed_name'].endswith('CANCELLED')
    assert novel['catalog_year']=='Fall 2024' and novel['description_digest']
    assert any('does not establish actual or current availability' in r for r in novel['restrictions'])
    foundations=[r for r in MANIFEST['courses'].values() if r['listed_code']=='21L.001']
    assert len(foundations)==2
    assert all(r['observations'][-1]['category']=='human_context' for r in foundations)
    path=Path('/tmp/mit-hass-subjects/literature-fall2024-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public Literature archive')
    hashes={review.observation_digest(o) for o in review.observe_literature(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-literature-fall2024']
    assert len(saved)==7 and all(o['observation_digest'] in hashes for o in saved)


def test_older_literature_spanish_language_does_not_invent_prerequisite():
    utopia=entry('21L.637J [21G.717]')['observations'][-1]
    conflict=entry('21L.638J [21G.738]')['observations'][-1]
    assert utopia['catalog_year']==conflict['catalog_year']=='Fall 2022'
    assert utopia['prerequisites']=='none'
    assert conflict['prerequisites']=='One intermediate subject in Spanish or permission of instructor'
    assert utopia['credits']==conflict['credits']==12
    assert any('no intermediate-Spanish requirement is inferred' in r for r in utopia['restrictions'])
    television=entry('21L.432J [CMS.315]')['observations'][-1]
    assert television['observed_name']=='Understanding Television'
    assert any('graduate version' in r for r in television['restrictions'])
    checks=[r for r in MANIFEST['source_checks'] if 'fall+2023' in r['url']]
    assert checks and 'CANCELLED' in checks[-1]['reason']


@pytest.mark.parametrize('term,count',[('fall2022',4),('spring2023',1)])
def test_older_literature_observations_replay(term,count):
    path=Path('/tmp/mit-hass-subjects')/f'literature-{term}-visible.html'
    if not path.exists():
        pytest.skip('Optional ignored public Literature archive')
    hashes={review.observation_digest(o) for o in review.observe_literature(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-literature-{term}']
    assert len(saved)==count and all(o['observation_digest'] in hashes for o in saved)


def test_literature_archive_accounting_and_spanish_incubator_actual_content():
    audit=MANIFEST['literature_archive_review']
    assert len(audit['semesters'])==len({r['term'] for r in audit['semesters']})==38
    assert set(audit['remaining_title_only_records'])=={'mit-ai-hass-american-studies-21l-632j','mit-ai-hass-cmsw-pool-external-21l-715'}
    assert all(r['description_panels']<=r['observed_panels'] for r in audit['semesters'])
    incubator=entry('21L.590')['observations'][-1]
    assert incubator['evidence_basis']=='official_description' and incubator['category']=='human_context'
    assert incubator['catalog_year']=='IAP 2025' and incubator['credits']==9
    assert incubator['prerequisites']=='none'
    assert any('Spanish is explicitly not a prerequisite' in r for r in incubator['restrictions'])
    assert any('priority registration' in r for r in incubator['restrictions'])
    arthur=entry('21L.460')['observations'][-1]
    assert arthur['catalog_year']=='Fall 2021' and arthur['prerequisites']=='One subject in Literature'
    darwin=entry('21L.022J [21W.739J]')['observations'][-1]
    assert darwin['category']=='human_context' and darwin['catalog_year']=='Fall 2014'


@pytest.mark.parametrize('term,count',[('fall2021',1),('spring2020',2),('fall2014',1),('iap2025',1)])
def test_latest_matching_archived_literature_descriptions_replay(term,count):
    path=Path('/tmp/mit-hass-subjects')/f'literature-{term}-visible.html'
    if not path.exists():
        pytest.skip('Optional ignored public Literature archive')
    hashes={review.observation_digest(o) for o in review.observe_literature(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-literature-{term}']
    assert len(saved)==count and all(o['observation_digest'] in hashes for o in saved)


def test_literature_same_subject_guard_is_not_meets_with_or_code_inference():
    html='''<select name="semester"><option selected>Spring 2026</option></select>
    <div class="parentrow"><a class="description-link" data-course="h">21L.500[J]</a><span>How We Got to Hamilton (New!)</span></div>
    <div class="description-row" data-course="h"><p>Same subject as: CMS.427[J], 21T.247[J] Prereq: none Units: 3-0-9</p><div class="et-l--post">Critical theater history.</div></div>'''
    o=review.observe_literature_aliases(html)[0]
    assert o['same_subject_as']=='CMS.427[J], 21T.247[J]' and o['meets_with'] is None
    assert review.observe_literature_aliases(html.replace('Same subject as:','Meets with:'))==[]
    assert review.observe_literature(html)[0].get('same_subject_as') is None  # old primary-code digest stays stable


def test_actual_hamilton_literature_description_withdraws_if_alias_clause_changes():
    path=Path('/tmp/mit-hass-subjects/literature-spring2026-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public Literature capture')
    o=next(o for o in review.observe_literature_aliases(path.read_text()) if o['code']=='21L.500[J]')
    assert o['description'] and o['same_subject_as']=='CMS.427[J], 21T.247[J]'
    rows=[(cid,r) for cid,r in MANIFEST['courses'].items() if r['listed_code'].startswith('CMS.427')]
    assert len(rows)==2
    for cid,r in rows:
        e=r['observations'][-1];course=dict(id=cid,code=r['listed_code'],name=r['listed_name'],source_id=r['listed_source_id'])
        assert e['category']=='human_context' and e['credits']==12 and e['prerequisites']=='none'
        assert review.matched_review(course,o,e['source_url'],MANIFEST)==e
        assert review.matched_review(course,{**o,'same_subject_as':'CMS.999[J]'},e['source_url'],MANIFEST) is None


def test_department_followup_distinguishes_login_heading_and_approval_barriers():
    checks=MANIFEST['source_checks']
    report=MANIFEST['department_followup_review']
    assert len(report['canvas_links'])==19
    assert report['public_heading_only_links']==16 and report['login_required_links']==3
    assert report['description_upgrades']==0
    login={r['url'] for r in checks if r.get('status')=='login_required'}
    assert login=={'https://canvas.mit.edu/courses/39652','https://canvas.mit.edu/courses/39685','https://canvas.mit.edu/courses/36626'}
    rejected=[r for r in checks if r.get('status')=='automatic_approval_review_rejected']
    assert len(rejected)==1 and rejected[0]['url']=='https://stellar.mit.edu/S/course/24/sp19/24.903'
    assert 'not a publisher denial' in rejected[0]['reason']
    assert 'independent public' in report['remaining_action']


def test_ocw_syllabus_guards_date_identity_description_and_prerequisite_semantics():
    html='''<div id="course-banner"><span class="course-number-term-detail">24.235J | Spring 2012 | Undergraduate</span><h1>Philosophy of Law</h1></div><div id="course-main-content"><h3>Prerequisites</h3><p>One philosophy subject is recommended.</p><h3>Course Description</h3><p>Law, morality and responsibility.</p><h3>Grading</h3><p>Three essays.</p></div>'''
    o=review.observe_ocw_syllabus(html)[0]
    assert o['description']=='Law, morality and responsibility.'
    assert o['prerequisites']=='One philosophy subject is recommended.'
    assert o['term']=='Spring 2012' and o['units'] is None
    with pytest.raises(ValueError,match='description'):
        review.observe_ocw_syllabus(html.replace('Course Description','Resources'))
    with pytest.raises(ValueError,match='term'):
        review.observe_ocw_syllabus(html.replace('Spring 2012','Undated'))
    absent=review.observe_ocw_syllabus(html.replace('<h3>Prerequisites</h3><p>One philosophy subject is recommended.</p>',''))[0]
    assert absent['prerequisites'] is None


def test_ocw_actual_manual_subjects_keep_mixed_content_and_historical_identity():
    report=MANIFEST['ocw_philosophy_review']
    assert report['directory_results_observed']==78
    assert report['public_course_pages_read']==report['public_syllabi_read']==17
    assert len(report['upgraded_record_ids'])==24
    decision=entry('24.222')['observations'][-1]
    assert decision['category']=='other' and decision['status']=='mixed'
    assert decision['candidate_categories']==['mathematics','human_context']
    assert decision['catalog_year']=='Spring 2008' and decision['credits'] is None
    phonology=entry('24.901')['observations'][-1]
    assert phonology['observed_name']=='Introduction to Phonology'
    assert phonology['catalog_year']=='Spring 2026'
    assert phonology['prerequisites']=='24.900 Introduction to Linguistics or 24.9000 Introduction to Linguistics'
    assert entry('24.9000')['observations'][-1]['evidence_basis']=='official_title_only'
    assert entry('24.130')['observations'][-1]['evidence_basis']=='official_title_only'
    assert entry('24.120')['observations'][-1]['observed_code']=='24.120'
    assert entry('24.120')['observations'][-1]['catalog_year']=='Spring 2009'
    assert 'recommended' in entry('24.235J/17.021J')['observations'][-1]['prerequisites']
    assert entry('24.02')['observations'][-1]['prerequisites'] is None
    assert entry('24.03')['observations'][-1]['prerequisites']=='None'


def test_actual_ocw_observations_replay_and_reject_changed_term_or_prerequisite():
    index=Path('/tmp/mit-hass-subjects/ocw-philosophy-syllabus-index.json')
    if not index.exists():
        pytest.skip('Optional ignored public OCW captures')
    seen=0
    for source in json.loads(index.read_text()):
        path=index.parent/('ocw-'+source['key']+'-syllabus.html')
        if not path.exists():
            pytest.skip('Optional ignored public OCW syllabus')
        o=review.observe_ocw_syllabus(path.read_text())[0]
        for cid,row in MANIFEST['courses'].items():
            e=next((e for e in row['observations'] if e['source_url']==source['url']),None)
            if e is None:continue
            course=dict(id=cid,code=row['listed_code'],name=row['listed_name'],source_id=row['listed_source_id'])
            assert review.matched_review(course,o,source['url'],MANIFEST)==e
            assert review.matched_review(course,{**o,'term':'Fall 2026'},source['url'],MANIFEST) is None
            assert review.matched_review(course,{**o,'prerequisites':'Changed condition'},source['url'],MANIFEST) is None
            seen+=1
    assert seen==23


def test_instructor_mind_description_requires_published_code_link():
    html='''<h1>Minds and Machines (Spring 2020)</h1><p>This course is an introduction to the central questions in philosophy of mind. Consciousness and representation.</p><a href="https://learning-modules.mit.edu/class/index.html?uuid=/course/24/sp20/24.09">Course site</a>'''
    o=review.observe_minds_machines(html)[0]
    assert o['code']=='24.09' and o['prerequisites'] is o['units'] is None
    with pytest.raises(ValueError,match='code link'):
        review.observe_minds_machines(html.replace('sp20/24.09','sp20/24.99'))
    assert entry('24.09')['observations'][-1]['category']=='human_context'


def test_political_ocw_preserves_permission_recommendations_and_code_boundaries():
    report=MANIFEST['ocw_political_review']
    assert report['directory_results_observed']==97
    assert report['public_course_pages_read']==report['public_syllabi_read']==22
    assert len(report['upgraded_record_ids'])==42
    middle=entry('17.568')['observations'][-1]
    assert middle['prerequisites']=='MIT students need the permission of the instructors.'
    assert any('Graduate course; advanced undergraduates' in text for text in middle['restrictions'])
    congress=entry('17.251')['observations'][-1]
    assert '4 or 5' in congress['prerequisites'] and '17.20' in congress['prerequisites']
    cyber=entry('17.445')['observations'][-1]
    assert 'Graduate students need the permission' in cyber['prerequisites']
    assert cyber['category']=='human_context'
    emerging=entry('17.449')['observations'][-1]
    assert emerging['category']=='human_context' and any('helpful but explicitly not required' in text for text in emerging['restrictions'])
    methods=entry('17.801')['observations'][-1]
    assert methods['category']=='human_context' and 'not data analysis' in ' '.join(methods['restrictions'])
    for code in ['17.447','17.483','17.803','17.811','17.567']:
        assert entry(code)['observations'][-1]['evidence_basis']=='official_title_only'
    composite=entry('17.565/17.567')['observations'][-1]
    assert composite['observed_code']=='17.565' and composite['credits'] is None
    assert any('distinct17.567' in text for text in composite['restrictions'])


def test_actual_political_ocw_observations_replay_with_changed_text_withdrawal():
    path=Path('/tmp/mit-hass-subjects/ocw-political-index.json')
    if not path.exists():
        pytest.skip('Optional ignored OCW Political Science captures')
    seen=0
    for source in json.loads(path.read_text()):
        if not source['key'].endswith('-syllabus'):continue
        cache=path.parent/('ocw-'+source['key']+'.html')
        if not cache.exists():pytest.skip('Optional ignored public syllabus')
        o=review.observe_ocw_syllabus(cache.read_text())[0]
        for cid,row in MANIFEST['courses'].items():
            e=next((e for e in row['observations'] if e['source_url']==source['url']),None)
            if e is None:continue
            c=dict(id=cid,code=row['listed_code'],name=row['listed_name'],source_id=row['listed_source_id'])
            assert review.matched_review(c,o,source['url'],MANIFEST)==e
            assert review.matched_review(c,{**o,'description':o['description']+' Changed.'},source['url'],MANIFEST) is None
            seen+=1
    assert seen==42


def test_history_home_description_never_borrows_syllabus_fields():
    html='''<div id="course-banner"><span class="course-number-term-detail">21H.132 | Spring 2017 | Undergraduate</span><h1>The Ancient World: Rome</h1></div><div id="expanded-description">Roman society and politics.<button>Show less</button></div>'''
    o=review.observe_ocw_course(html)[0]
    assert o['description']=='Roman society and politics.'
    assert o['prerequisites'] is o['units'] is None
    with pytest.raises(ValueError,match='complete description'):
        review.observe_ocw_course(html.replace('expanded-description','collapsed-description'))
    rome=entry('21H.132')['observations'][-1]
    assert rome['prerequisites'] is None and any('separate Spring2017syllabus' in t for t in rome['restrictions'])
    samurai=entry('21H.154')['observations'][-1]
    assert 'meets with 21G.554' in samurai['prerequisites']
    assert any('No identity merge' in t for t in samurai['restrictions'])
    assert samurai['category']=='human_context'
    assert MANIFEST['courses']['mit-ai-hass-russian-and-eurasian-studies-21h-245j']['review_status']=='identity_review_needed'


def test_actual_history_observations_replay_and_keep_separate_identity_hold():
    report=MANIFEST['ocw_history_review']
    assert report['directory_results_observed']==92
    assert report['public_course_pages_read']==report['public_syllabi_read']==14
    assert len(report['upgraded_record_ids'])==16
    path=Path('/tmp/mit-hass-subjects/ocw-history-index.json')
    if not path.exists():pytest.skip('Optional ignored public OCW captures')
    seen=0
    for source in json.loads(path.read_text()):
        home=source['key'].startswith(('21h-101-','21h-132-'))
        if home==source['key'].endswith('-syllabus'):continue
        cache=path.parent/('ocw-'+source['key']+'.html')
        if not cache.exists():pytest.skip('Optional ignored public course capture')
        o=(review.observe_ocw_course if home else review.observe_ocw_syllabus)(cache.read_text())[0]
        for cid,row in MANIFEST['courses'].items():
            e=next((e for e in row['observations'] if e['source_url']==source['url']),None)
            if e is None:continue
            c=dict(id=cid,code=row['listed_code'],name=row['listed_name'],source_id=row['listed_source_id'])
            assert review.matched_review(c,o,source['url'],MANIFEST)==e
            assert review.matched_review(c,{**o,'code':'21H.999'},source['url'],MANIFEST) is None
            seen+=1
    assert seen==16


def test_anthropology_ocw_historical_nine_units_and_nonmerged_renumbered_courses():
    report=MANIFEST['ocw_anthropology_review']
    assert report['directory_results_observed']==67
    assert report['public_course_pages_read']==report['public_syllabi_read']==9
    assert len(report['upgraded_record_ids'])==14
    tech=entry('21A.500J')['observations'][-1]
    assert tech['credits']==9 and tech['credit_unit']=='units'
    assert tech['units_text']=='9 units' and tech['catalog_year']=='Spring 2014'
    assert tech['category']=='human_context'
    meaning=entry('21A.157')['observations'][-1]
    assert meaning['evidence_basis']=='official_description' and meaning['category']=='human_context'
    assert entry('21A.504J')['observations'][-1]['evidence_basis']=='official_title_only'
    assert entry('21A.508')['observations'][-1]['evidence_basis']=='official_title_only'


def test_actual_anthropology_observer_h5_and_explicit_unit_amount_replay():
    path=Path('/tmp/mit-hass-subjects/ocw-anthropology-index.json')
    if not path.exists():pytest.skip('Optional ignored OCW Anthropology captures')
    seen=0
    for source in json.loads(path.read_text()):
        if not source['key'].endswith('-syllabus'):continue
        cache=path.parent/('ocw-'+source['key']+'.html')
        if not cache.exists():pytest.skip('Optional ignored public syllabus')
        html=cache.read_text();o=review.observe_ocw_syllabus(html)[0]
        if o['code']=='21A.500J':
            assert o['units']=='9 units'
            assert review.observe_ocw_syllabus(html.replace('This 9-unit subject','This subject'))[0]['units'] is None
        if o['code']=='21A.520':
            assert o['description'].startswith('This course explores magic') and 'Code of Conduct' not in o['description']
            assert o['prerequisites']=='There are no prerequisites for this course.'
        for cid,row in MANIFEST['courses'].items():
            e=next((e for e in row['observations'] if e['source_url']==source['url']),None)
            if e is None:continue
            c=dict(id=cid,code=row['listed_code'],name=row['listed_name'],source_id=row['listed_source_id'])
            assert review.matched_review(c,o,source['url'],MANIFEST)==e
            seen+=1
    assert seen==14


def test_economics_actual_subject_focus_dated_identity_and_preparation_strength():
    report=MANIFEST['ocw_economics_review']
    assert report['directory_results_observed']==77
    assert report['public_course_pages_read']==report['public_syllabi_read']==17
    assert len(report['upgraded_record_ids'])==23
    for code in ['14.12','14.15[J]','14.16']:
        assert entry(code)['observations'][-1]['category']=='mathematics'
    mixed=entry('14.03')['observations'][-1]
    assert mixed['category']=='other' and mixed['status']=='mixed'
    assert mixed['candidate_categories']==['mathematics','human_context']
    for code in ['14.04','14.20','14.44','14.54']:
        assert entry(code)['observations'][-1]['category']=='applications'
    assert entry('14.73')['observations'][-1]['category']=='human_context'
    assert 'no programming prerequisite' in entry('14.15[J]')['observations'][-1]['prerequisites']
    assert 'recommended but not required' in entry('14.75')['observations'][-1]['prerequisites']
    assert 'Econometrics is not a prerequisite' in entry('14.74')['observations'][-1]['prerequisites']
    assert entry('14.74')['observations'][-1]['observed_name']=='Foundations of Development Policy'
    assert entry('14.74')['listed_name']=='Foundations of Development Economics'
    assert entry('14.27')['observations'][-1]['evidence_basis']=='official_title_only'
    assert entry('14.42')['observations'][-1]['prerequisites'] is None
    for code in ['14.01','14.02','14.13','14.16','14.73']:
        e=entry(code)['observations'][-1]
        assert e['prerequisites'] is None
        assert any('Separate ' in x and 'syllabus prerequisite evidence' in x for x in e['restrictions'])
    assert all(entry(code)['observations'][-1]['credits'] is None for code in ['14.01','14.12','14.16','14.73'])


def test_ocw_description_excludes_separate_mitx_course_and_guards_embedded_prerequisite():
    banner='<div id="course-banner"><span class="course-number-term-detail">14.73 | Spring 2011 | Undergraduate</span><h1>The Challenge of World Poverty</h1></div>'
    body='<div id="expanded-description"><p>Poverty and public policy.</p><p><strong>MITx Online Version</strong></p><p>Create an account for14.73x.</p></div>'
    assert review.observe_ocw_course(banner+body)[0]['description']=='Poverty and public policy.'
    banner=banner.replace('14.73','14.20').replace('Spring 2011','Spring 2003')
    syllabus='<div id="course-main-content"><h2>Introduction</h2><p>Industrial economics. Students must have completed microeconomics at the level of 14.01 before enrolling in 14.20.</p><h2>Grading</h2><p>Exams.</p></div>'
    o=review.observe_ocw_syllabus(banner+syllabus)[0]
    assert o['prerequisites']=='Students must have completed microeconomics at the level of 14.01 before enrolling in 14.20.'
    assert 'Grading' not in o['description']
    assert review.observe_ocw_syllabus((banner+syllabus).replace('must have completed','may have completed'))[0]['prerequisites'] is None


def test_actual_economics_sources_replay_without_collapsing_page_provenance():
    path=Path('/tmp/mit-hass-subjects/ocw-economics-index.json')
    if not path.exists():pytest.skip('Optional ignored public OCW Economics captures')
    seen=0
    for source in json.loads(path.read_text()):
        home=source['key'].startswith(('14-01-','14-02-','14-13-','14-16-','14-73-'))
        if home==source['key'].endswith('-syllabus'):continue
        cache=path.parent/('ocw-'+source['key']+'.html')
        if not cache.exists():pytest.skip('Optional ignored course capture')
        o=(review.observe_ocw_course if home else review.observe_ocw_syllabus)(cache.read_text())[0]
        if o['code']=='14.20':assert o['prerequisites'].startswith('Students must have completed')
        if o['code']=='14.73':assert 'MITx' not in o['description']
        for cid,row in MANIFEST['courses'].items():
            e=next((e for e in row['observations'] if e['source_url']==source['url']),None)
            if e is None:continue
            c=dict(id=cid,code=row['listed_code'],name=row['listed_name'],source_id=row['listed_source_id'])
            assert review.matched_review(c,o,source['url'],MANIFEST)==e
            assert review.matched_review(c,{**o,'term':'Spring 2099'},source['url'],MANIFEST) is None
            seen+=1
    assert seen==23


def test_urban_dated_title_permissions_and_mixed_domain_subjects():
    report=MANIFEST['ocw_urban_review']
    assert report['directory_results_observed']==199
    assert report['public_course_pages_read']==report['public_syllabi_read']==16
    assert len(report['upgraded_record_ids'])==14
    assert len(report['withheld_description_reads'])==4
    current=entry('11.013[J]')['observations'][-1]
    old=entry('11.013J [21H.217]')['observations'][-1]
    assert (current['catalog_year'],current['credits'],current['credit_unit'])==('Spring 2025',12,'units')
    assert old['catalog_year']=='Spring 2010' and old['credits'] is None
    assert current['observed_name']=='American Urban History' and old['observed_name']=='American Urban History I'
    assert 'permission of the instructor' in entry('11.166')['observations'][-1]['prerequisites']
    assert 'OCW users do not need permission' in entry('11.166')['observations'][-1]['prerequisites']
    assert entry('11.011')['observations'][-1]['category']=='human_context'
    assert entry('11.001[J]')['observations'][-1]['category']=='applications'
    for code in ['11.123','11.165']:
        e=entry(code)['observations'][-1]
        assert e['category']=='other' and e['status']=='mixed'
        assert e['candidate_categories']==['applications','human_context']
    for code in ['11.041','11.148','11.015[J]','11.025[J]']:
        assert entry(code)['observations'][-1]['evidence_basis']=='official_title_only'


def test_urban_actual_captures_replay_and_historical_unit_amount_is_guarded():
    path=Path('/tmp/mit-hass-subjects/ocw-urban-index.json')
    if not path.exists():pytest.skip('Optional ignored public OCW Urban Studies captures')
    seen=0
    for source in json.loads(path.read_text()):
        if not source['key'].endswith('-syllabus'):continue
        cache=path.parent/('ocw-'+source['key']+'.html')
        if not cache.exists():pytest.skip('Optional ignored public syllabus')
        html=cache.read_text();o=review.observe_ocw_syllabus(html)[0]
        if o['code']=='11.013J' and o['term']=='Spring 2025':
            assert o['units']=='12 units'
            assert review.observe_ocw_syllabus(html.replace('This 12-unit undergraduate-level course','This undergraduate-level course'))[0]['units'] is None
        for cid,row in MANIFEST['courses'].items():
            e=next((e for e in row['observations'] if e['source_url']==source['url']),None)
            if e is None:continue
            c=dict(id=cid,code=row['listed_code'],name=row['listed_name'],source_id=row['listed_source_id'])
            assert review.matched_review(c,o,source['url'],MANIFEST)==e
            assert review.matched_review(c,{**o,'prerequisites':'Permission no longer required'},source['url'],MANIFEST) is None
            seen+=1
    assert seen==14
