"""Observe reviewed Miami enrollment/degree-policy scopes without granting approval."""
from functools import partial
import hashlib
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean
from atlas.adapters.national_curriculum_common import rule
from atlas.adapters.miami_policies import SPECS, parse_policy

PROGRAMS={
 'miami-data-science-ai-bs','miami-ai-technologies-business-bsba',
 'university-of-miami-data-science-and-artificial-intelligence-ba-degree',
 'university-of-miami-artificial-intelligence-technologies-for-business-other-degree'}
HASHES={'courses':'8a5c61a97abef5b466bb3fa06938adf561abd6af7d1b897a37f6985bd1583dd6',
        'graduation':'3c52ab8bbc9fe59c252893681c12921368b15fddfc534fe63596bd79c59f5da0'}
SOURCE_IDS={'courses':'miami-course-information-policy','graduation':'miami-graduation-policy'}
NOTES={
 'courses':[
 ('credit-unit-and-level','Semester credits and course-level eligibility',
  'Miami uses a semester system and explicitly treats academic credits, semester credits, semester hours, credit hours and hours as names for its academic credit measure. The policy applies across credit-bearing formats; laboratory/studio contact hours are not additional academic credits. The 500 series is open only to seniors or other qualified undergraduates; 600–800 courses are open only to graduate students. A contextual course listing does not establish individual qualification or waive its own prerequisites.'),
 ('registration-permission','Registration permission and enrollment confirmation',
  'Some adds require professor or department permission, supplied through a PIN or signed Drop/Add form and processed by the student or Canes Central; faculty cannot themselves enroll a student. Students must verify successful enrollment and correct course credits by the last day to drop without a W. A request or permission alone is not completed enrollment, and the policy does not promise a prerequisite override.'),
 ('modality-limits','Conditional online-course limits for in-person programs',
  'Students normally take courses in their admitted program modality. For an in-person program, the published exception permits at most one online course in a full-time fall/spring schedule, with winter/spring intersessions counted in spring, and up to nine online credits in summer. Online credits cannot exceed 25 percent of the credential total and no fall/spring term may be wholly online. International-student restrictions may be additional; modality approval is not inferred from catalog membership.'),
 ('credit-only-recording','Credit-only timing and recorded credit',
  'The credit-only election deadline is two weeks after the last registration day for fall/spring and the last drop-without-W day in summer; later changes are limited to withdrawal. A through C-minus become CR; D/F become NC without credits or quality points. Existing eligibility and free-elective restrictions remain controlling. Writing courses WRS105/106/107 and ENG106 cannot be elected credit-only.')],
 'graduation':[
 ('declaration-processing','Declaration and degree-change completion',
  'Students declare the major, minor and/or cognate required by their own degree through the school process. Calendar deadlines require the declaration or degree/major change to be processed in CaneLink, not merely requested. Changes may alter the applicability of prior coursework. The student-specific Degree Progress Report is not accessed or assumed here.'),
 ('conditional-dual-degree','Optional dual-degree route and approval',
  'Two majors normally produce one degree based on the primary major. An optional second degree requires a different degree and major, at least 150 credits (possibly more), all requirements for both except university general education completed once, and distinct majors/minors where required across schools. Final approval comes from the Dean of Undergraduate Education before the first degree is conferred. This optional route does not increase the single degree’s published minimum or grant approval.'),
 ('nonregistration-credit-scope','Conditional military and nonregistration credit',
  'The university graduation policy caps combined correspondence/extension work at 30 credits, excludes it from the final 45 and requires departmental evaluation. It caps military-experience credit at 30, subject to individual acceptance and degree applicability. Test and other nonregistration credit need appropriate departmental approval and cannot satisfy final-45 residence. These ceilings do not grant credit, supersede a narrower transfer category or turn military schooling and experience into the same category.')]
}


def parse(html, *, pid, key):
    if pid not in PROGRAMS or key not in HASHES:raise ValueError('Unreviewed Miami degree-policy scope')
    observed=parse_policy(html,pid=pid,code=key)
    content=BeautifulSoup(html,'html.parser').select_one('#content')
    for nav in content.find_all('nav'):nav.decompose()
    if hashlib.sha256(clean(content.get_text(' ',strip=True)).encode()).hexdigest()!=HASHES[key]:
        raise ValueError('Miami reviewed policy changed; source review required')
    return {**observed,'requirements':[rule(pid+'-policy-'+suffix,title,SOURCE_IDS[key],kind='note',summary=summary) for suffix,title,summary in NOTES[key]]}


def _compose(previous, html, *, pid, key):
    old=previous(html);new=parse(html,pid=pid,key=key)
    if old.get('id')!=pid:raise ValueError('Wrong prior Miami policy identity')
    ids={r['id']for r in new['requirements']}
    if ids & {r['id']for r in old.get('requirements',[])}:raise ValueError('Duplicate Miami policy note')
    return {**old,'requirements':old.get('requirements',[])+new['requirements'],
            'observed_policy_sections':{**old.get('observed_policy_sections',{}),**new['observed_policy_sections']}}


def register(pid,sources,parsers):
    if pid not in PROGRAMS:raise ValueError('Unreviewed Miami program')
    for key in HASHES:
        url=SPECS[key][0]
        if url not in sources:sources.append(url)
        previous=parsers.get(url)
        parsers[url]=partial(_compose,previous,pid=pid,key=key) if previous else partial(parse,pid=pid,key=key)
