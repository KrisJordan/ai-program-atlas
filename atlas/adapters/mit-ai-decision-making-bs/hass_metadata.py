"""Integrate guarded departmental HASS observations without certifying a review."""
import json
from pathlib import Path
from importlib import import_module
from atlas.adapters.national_curriculum_common import course, rule

PID='mit-ai-decision-making-bs'
observer=import_module('atlas.adapters.mit-ai-decision-making-bs.reviewed_hass_subjects')
public_resources=import_module('atlas.adapters.mit-ai-decision-making-bs.public_resources')
MANIFEST=json.loads(Path(__file__).with_name('reviewed_hass_subjects.json').read_text())
PARSERS={k:getattr(observer,'observe_'+k)for k in ['architecture','literature','history','wgs','wgs_detail','performing_arts','cmsw','language_titles','political_pdf_titles','sts_titles','anthropology_titles','economics_titles','shass_field_titles','remaining_list_titles','french_spotlights','literature_aliases','ocw_syllabus','minds_machines','ocw_course','ocw_language_syllabus','music_semester_capture','theater_semester_capture','concourse_subject','wgs_archive_detail','dlab_course','sts_department_detail','urban_project_course','common_ground_subject','political_methods_syllabus']}
INTEGRATED=json.loads(Path(__file__).with_name('integrated_hass_scope.json').read_text())
SPECS={sid:MANIFEST['source_specs'][sid]for sid in INTEGRATED['source_ids']}


def parse(html,url):
    specs=[s for s in SPECS.values()if s['url']==url]
    spec=specs[0]
    observations=[];seen=set()
    captured_input=html.lstrip().startswith('{')
    for source in specs:
        capture_parser=source['parser'] in {'music_semester_capture','theater_semester_capture'}
        if capture_parser != captured_input:continue
        signature=(source['parser'],source.get('field_key'),source.get('source_kind'))
        if signature in seen:continue
        seen.add(signature)
        parser=PARSERS[source['parser']]
        found=(parser(source['field_key'],html) if source['parser']=='shass_field_titles'
               else parser(source['source_kind'],html) if source['parser']=='remaining_list_titles' else parser(html))
        observations.extend([found] if isinstance(found,dict) else found)
    rows=[];digests={}
    for cid in INTEGRATED['course_ids']:
        r=MANIFEST['courses'][cid]
        if r['review_status']!='reviewed' or not any(o['source_url']==url and o['approved_for_integration']for o in r['observations']):continue
        listed=dict(id=cid,code=r['listed_code'],name=r['listed_name'],source_id=r['listed_source_id'])
        matches=[(o,observer.matched_review(listed,o,url,MANIFEST))for o in observations]
        matches=[(o,review)for o,review in matches if review]
        if not matches:continue  # changed evidence stays a missing observation for review
        o,review=matches[0]
        c=course('mit-ai-hass',r['listed_code'],r['listed_name'],review['source_id'],url,unit='units');c['id']=cid
        c.update(category=review['category'],description=review['description_summary'],prerequisites=review['prerequisites'],credits=review['credits'])
        c.update(public_resources.observed_resources(cid,url))
        c['notes']=list(review['restrictions'])
        if review.get('evidence_basis') == 'official_title_only':
            c['notes'].append('Limited official-title-only classification; no course description was verified. Credit or prerequisite fields require separately explicit source observations.')
        if review.get('evidence_basis') == 'official_code_only':
            c['notes'].append('Official code-only observation; title, description and content classification remain unknown.')
        c['notes'].append('Observed departmental source term/version: '+str(review['catalog_year']or'not stated')+'. The original list identity is retained.')
        if review.get('identity_note'):c['notes'].append(review['identity_note'])
        rows.append(c);digests[cid]=observer.observation_digest(o)
    rules=[]
    if spec['parser']=='literature':
        by={o['code']:o for o in observations}
        if all(code in by for code in ['21L.607','21L.608','21L.613','21L.614']):
            greek=by['21L.607']['description']+' '+by['21L.608']['description']
            latin=by['21L.613']['description']+' '+by['21L.614']['description']
            if 'after completion of both'in greek and 'single HASS-H'in greek and 'by petition'in latin and 'two terms of 21L.614'in latin:
                rules.append(rule('mit-ai-hass-reviewed-language-bundles','Departmental half-term language combinations','mit-ai-hass-review-literature',kind='note',summary='Greek21L.607 and608 may combine after both are completed as one HASS-H. Latin21L.613+614, or two terms of614, may combine by petition after completion as one HASS-H;614 may be repeated once only if content differs. Separate six-unit subject records remain distinct and are not each treated as a full twelve-unit HASS subject.'))
    return dict(id=PID,courses=rows,requirements=rules,observed_hass_description_digests=digests)


SOURCE_PARSERS={s['url']:(lambda html,url=s['url']:parse(html,url))for s in SPECS.values()}


def with_metadata(primary, secondary):
    """Keep a shared page's existing eligibility rules when adding metadata."""
    def combined(html):
        base = primary(html)
        extra = secondary(html)
        courses = {c['id']: c for c in base.get('courses', [])}
        for c in extra.get('courses', []):
            if c['id'] not in courses:
                courses[c['id']] = c
                continue
            old = courses[c['id']]
            notes = list(dict.fromkeys(old.get('notes', []) + c.get('notes', [])))
            old.update({k: v for k, v in c.items() if v is not None})
            old['notes'] = notes
        return {**base, **{k: v for k, v in extra.items() if k not in {'courses', 'requirements'}},
                'courses': list(courses.values()),
                'requirements': base.get('requirements', []) + extra.get('requirements', [])}
    return combined
