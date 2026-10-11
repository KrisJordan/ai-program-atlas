"""Observe public W&M policy pages; PDF text requires a separate reviewed extraction."""
import hashlib
from atlas.adapters.national_curriculum_common import clean, content

ADVISING = 'https://www.wm.edu/offices/advising/academic-forms/'
MAJOR_PDF = 'https://www.wm.edu/offices/registrar/_documents/degree/declaration_of_major_form.pdf'
MINOR_PDF = 'https://www.wm.edu/offices/registrar/_documents/degree/declaration_of_academic_minor.pdf'


def parse_advising(html, pid):
    root = content(html, 'Academic Forms & Processes')
    sections = {}
    for title in ['Form Categories', 'Registrar Forms']:
        heading = next((h for h in root.find_all(['h2', 'h3']) if clean(h.get_text()) == title), None)
        if not heading:
            raise ValueError('W&M policy section missing: ' + title)
        values = []
        for sibling in heading.next_siblings:
            if getattr(sibling, 'name', None) in ('h2', 'h3'):
                break
            values.append(sibling.get_text(' ', strip=True) if hasattr(sibling, 'get_text') else str(sibling))
        value = clean(' '.join(values))
        if len(value) < 80:
            raise ValueError('W&M policy section incomplete: ' + title)
        sections[title] = hashlib.sha256(value.encode()).hexdigest()
    return dict(id=pid, courses=[], requirements=[], observed_policy_sections=sections)


def parse_reviewed_declaration_text(text, pid, *, minor):
    """Manual format boundary: feed text extracted from the visually reviewed official PDF.

    The standard HTTP scraper accepts text/HTML, not PDF bytes. This function
    does not fetch, decode bytes, certify requirements, or emit a review audit.
    """
    if not isinstance(text, str):
        raise ValueError('Reviewed PDF text must be a string')
    value = clean(text)
    markers = ('DECLARATION OF ACADEMIC MINOR', 'Signature of Department Chair or Program Director') if minor else ('DECLARATION/CHANGE OF MAJOR', 'To Declare a Major', 'SINGLE VS. DOUBLE MAJORS')
    if any(marker not in value for marker in markers) or len(value) < 300:
        raise ValueError('W&M declaration PDF identity or text incomplete')
    return dict(id=pid, courses=[], requirements=[], observed_pdf_text_sha256=hashlib.sha256(value.encode()).hexdigest())
