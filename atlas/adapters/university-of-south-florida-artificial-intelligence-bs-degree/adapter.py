"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-south-florida-artificial-intelligence-bs-degree'
SOURCES = ('https://www.usf.edu/ai-cybersecurity-computing/academics/undergraduate/bsai.aspx', 'https://www.usf.edu/ai-cybersecurity-computing/documents/brochures/bellini-ug-bsai.pdf')

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='BSAI', kind='degree', aliases=(), award_terms=())


DEGREEWORKS_URL = 'https://www.usf.edu/registrar/register/degreeworks.aspx'
FAQ_URL = 'https://www.usf.edu/registrar/faq/index.aspx'
SOURCES += (DEGREEWORKS_URL, FAQ_URL)

def parse_degreeworks(html):
    import re
    from atlas.adapters.national_curriculum_common import content, clean, require_phrases, rule
    root = content(html, 'Credit Hour Breakdown')
    require_phrases(root, ['Degree Works', 'Total degree requirement', 'Upper-level requirement', 'Summer requirement', 'Residency requirement'])
    text = clean(root.get_text(' ', strip=True))
    patterns = [('total', r'(\d+): Total degree requirement', 'University minimum degree credits'),
                ('upper', r'(\d+): Upper-level requirement', 'University minimum upper-level credits'),
                ('summer', r'(\d+): Summer requirement', 'Published summer-enrollment minimum')]
    groups = []
    for key, pattern, title in patterns:
        match = re.search(pattern, text)
        if not match: raise ValueError('Credit breakdown changed: '+key)
        amount = int(match[1])
        summary = f'Registrar overview gives {amount} credit hours for this university requirement; program-specific requirements may be stricter. The normalized unit and detailed applicability remain unverified.'
        if key == 'summer': summary += ' The registrar FAQ permits documented waiver requests; entry-cohort exceptions remain unresolved.'
        groups.append(rule('usf-ai-university-'+key, title, 'usf-ai-degreeworks', kind='note', credits=amount, summary=summary))
    match = re.search(r'(\d+)/(\d+): Residency requirement \((\d+) of your last (\d+) must be completed at USF\)', text)
    if not match or match[1] != match[3] or match[2] != match[4]: raise ValueError('Residency rule changed or inconsistent')
    groups.append(rule('usf-ai-university-residence', 'University final-credit residency', 'usf-ai-degreeworks', kind='note', summary=f'Complete {match[1]} of the final {match[2]} credit hours at USF according to the registrar overview. Additional major/college residency requirements remain unverified.'))
    return dict(id=PROGRAM_ID, requirements=groups)

def parse_registrar_faq(html):
    from atlas.adapters.national_curriculum_common import content, require_phrases, rule
    root = content(html, 'Can I be excluded from the summer enrollment requirement?')
    require_phrases(root, ['Summer employment documented on official employer letterhead every summer term not enrolled', 'seasonal employment only during summer', 'Academic program courses unavailable summer terms', 'Unusual hardship due to exceptional circumstances', 'supporting documentation', 'during the semester in which you apply to graduate', 'Allow 3 weeks', 'original and the repeat course must be taken at USF', 'three Grade Forgivenesses', 'no more than one repeat per course', '"D" or higher', '"FF" grade indicating academic dishonesty', "Once a student is awarded a bachelor's degree"])
    sid = 'usf-ai-registrar-faq'
    return dict(id=PROGRAM_ID, requirements=[
        rule('usf-ai-summer-waiver', 'Conditional summer-enrollment waiver', sid, kind='note', summary='A waiver may be requested for documented seasonal summer employment in each summer missed, unavailable program courses certified by an advisor, or exceptional hardship outside the student’s control. Submit supporting evidence during the graduation-application semester; allow three weeks for a decision. A request is not automatic approval.'),
        rule('usf-ai-grade-forgiveness', 'Grade-forgiveness limits', sid, kind='note', summary='Both attempts must be at USF; the repeat grade must be at least D. At most three forgiveness uses are allowed, with one repeat per course. Academic-dishonesty FF grades are excluded, and forgiveness cannot change courses counted toward an already awarded bachelor’s degree. This does not establish AI-major passing grades.')])

SOURCE_PARSERS = {SOURCES[0]: parse, DEGREEWORKS_URL: parse_degreeworks, FAQ_URL: parse_registrar_faq}


# Absolute imports also support the project's standalone adapter loaders.
from importlib import import_module
_university = import_module('atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.university_policies')
_metadata = import_module('atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.course_metadata')
SOURCE_PARSERS.update(_university.PARSERS)
SOURCE_PARSERS.update(_metadata.PARSERS)
SOURCES += tuple(_university.PARSERS) + tuple(_metadata.PARSERS)

_remaining = import_module('atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.remaining_courses')
SOURCE_PARSERS.update(_remaining.PARSERS)
SOURCES += tuple(_remaining.PARSERS)

_entry = import_module('atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.entry_progression_policies')
SOURCE_PARSERS.update(_entry.PARSERS)
SOURCES += tuple(_entry.PARSERS)
