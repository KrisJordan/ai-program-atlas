"""Bounded transition statements, without extending a school-specific waiver."""
from functools import partial
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean, require_phrases, rule
from atlas.adapters.stevens_degree_course_review import PID

SOURCES = {
    'faq': 'https://www.stevens.edu/school-computing/frequently-asked-questions',
    'communications': 'https://www.stevens.edu/school-computing/communications',
}
SUMMARY = ('The School of Computing transition targets Fall 2026. The public transition '
           'guidance identifies computer science, AI and cybersecurity as initial programs, '
           'but its explicit unchanged-degree/curriculum assurance addresses current computer '
           'science students. It does not expressly assign the AI degree to the SES/Business '
           'arts-humanities list or school-scoped AP Calculus routes. Preserve those scope '
           'questions; the school launch is not evidence of the AI program launch date.')


def parse(html, kind):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    if main is None:
        raise ValueError('Stevens transition content missing')
    text = clean(main.get_text(' ', strip=True))
    phrases = ['School of Computing', 'Fall 2026', 'Current computer science majors',
               'their degrees and academic progress remain unchanged']
    if kind == 'faq':
        phrases += ['artificial intelligence and cybersecurity', 'Existing faculty, students and curricula will continue without disruption']
    elif kind == 'communications':
        phrases += ['Dec. 16, 2025', 'existing faculty, students and curricula continuing without disruption']
    else:
        raise ValueError('Unknown Stevens transition source')
    require_phrases(main, phrases)
    # A newly explicit answer to these questions must be reviewed, not ignored.
    if any(term in text.lower() for term in ('advanced placement', 'calculus', 'humanities credit')):
        raise ValueError('Stevens transition policy scope needs renewed review')
    return {'id': PID, 'courses': [], 'requirements': [rule(
        PID+'-school-transition-scope', 'School transition and policy applicability',
        PID+'-transition-'+kind, kind='note', summary=SUMMARY)]}


def register(sources, parsers):
    for kind, url in SOURCES.items():
        if url in parsers:
            raise ValueError('Duplicate Stevens transition observer')
        if url not in sources:
            sources.append(url)
        parsers[url] = partial(parse, kind=kind)
