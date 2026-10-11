"""Observe Vanderbilt's public GenAI overview; never infer missing quantities."""
import re
from bs4 import BeautifulSoup

PROGRAM_ID = "vanderbilt-genai-minor"
SOURCE_ID = "vanderbilt-genai-overview"
SOURCES = ("https://computing.vanderbilt.edu/genai-minor/",)
CATALOG_URL = "https://www.vanderbilt.edu/catalogs/kuali/undergraduate-26-27/#/content/69861623adcd935bcbec06a7"
CATALOG_SOURCE_ID = "vanderbilt-genai-catalog"


def clean(node):
    return " ".join(node.get_text(" ", strip=True).split())


def course(code, name, category):
    return dict(id="vanderbilt-" + code.lower().replace(" ", "-"), code=code,
                name=name, description=None, prerequisites=None, credits=None,
                credit_unit="unknown", category=category, source_id=SOURCE_ID,
                url=SOURCES[0], public_site=None, syllabus=None)


def requirement(suffix, title, kind, summary, ids=()):
    return dict(id=PROGRAM_ID + "-" + suffix, parent_id=None, title=title,
                kind=kind, count=None, credits=None, credit_unit="unknown",
                category="other", source_id=SOURCE_ID, source_text=None,
                summary=summary, course_ids=list(ids))


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("h1") or clean(soup.find("h1")) != "Join the GenAI Minor":
        raise ValueError("Vanderbilt GenAI minor identity missing")
    heading = next((h for h in soup.find_all("h2") if clean(h) == "Required Courses"), None)
    if heading is None:
        raise ValueError("Required Courses heading missing")
    block = heading.find_next_sibling()
    courses, core, integrated = [], [], []
    for item in block.find_all("details"):
        label = clean(item.find("summary"))
        match = re.fullmatch(r"(AI \d{4}):\s*(.+)", label)
        if match:
            code, name = match.groups()
            c = course(code, name, "human_context" if "Ethics" in name else "ai_ml")
            courses.append(c)
            core.append(c["id"])
        elif label == "AI-integrated course":
            for li in item.find_all("li"):
                match = re.fullmatch(r"([A-Z]+ \d{4})\s*[:–-]\s*(.+)", clean(li))
                if not match:
                    raise ValueError("Unrecognized integrated course entry")
                c = course(*match.groups(), "applications")
                courses.append(c)
                integrated.append(c["id"])
            if not all(p in clean(item) for p in ("Other courses may count", "submit the syllabus", "for review")):
                raise ValueError("Integrated-course approval route changed")
    if len(core) != 3 or not integrated or len({c['id'] for c in courses}) != len(courses):
        raise ValueError("Required-course structure changed; review needed")
    text = clean(soup)
    if "non-CS students" not in text:
        raise ValueError("Audience statement changed")
    return dict(id=PROGRAM_ID, title="GenAI", award_level="minor", program_kind="minor",
                curriculum_status="partial", courses=courses,
                requirements=[
                    requirement("core", "Named required AI courses", "all", "Complete the three named required courses.", core),
                    requirement("integrated", "AI-integrated course options — quantity unverified", "note", "The required-course section lists these integrated options but does not explicitly state the number or credits to select.", integrated),
                    requirement("approval", "Other integrated-course approval", "note", "Other courses can be reviewed when AI is a core method producing disciplinary insight, ideally with ethical engagement. Submit the syllabus to the college advising office for review."),
                    requirement("audience", "Designed for non-CS students", "note", "The page identifies non-CS students as the audience; formal eligibility and home-college restrictions remain unverified.")],
                notes=["Overview observation only: total credits, integrated-course quantity, general policies and formal CS-major eligibility require catalog review."])


def parse_catalog(html: str) -> dict:
    """Accept rendered public catalog HTML, not the empty Kuali HTTP shell."""
    soup = BeautifulSoup(html, "html.parser")
    heading = next((h for h in soup.find_all('h3') if clean(h) == 'Generative Artificial Intelligence Minor'), None)
    if heading is None:
        raise ValueError('Rendered Generative Artificial Intelligence section missing')
    parts = [heading]
    for sibling in heading.next_siblings:
        if getattr(sibling, 'name', None) == 'h3':
            break
        if getattr(sibling, 'name', None):
            parts.append(sibling)
    section = BeautifulSoup(''.join(str(p) for p in parts), 'html.parser')
    text = clean(section)
    if 'requires 12 hours' not in text or 'AI Applications and Evaluation' not in text:
        raise ValueError('Catalog total or application section changed')
    table = section.find('table')
    rows = [clean(r) for r in table.find_all('tr')] if table else []
    if len(rows) != 5 or not all('3 hours' in r for r in rows[:4]):
        raise ValueError('Catalog requirement table changed')
    courses, requirements = [], []
    for index in range(2):
        match = re.search(r'(AI \d{4}) (.+?) 3 hours', rows[index])
        if not match:
            raise ValueError('Catalog core row missing')
        c = course(*match.groups(), 'ai_ml')
        c.update(source_id=CATALOG_SOURCE_ID, url=CATALOG_URL, credits=3)
        courses.append(c)
    ethics = re.findall(r'(?:AI|HIST|PHIL) \d{4}', rows[2])
    if 'one of' not in rows[2] or len(ethics) != 4 or 'One course from AI Applications and Evaluation' not in rows[3]:
        raise ValueError('Catalog choice rules changed')
    for code in ethics:
        c = course(code, 'Ethics of Generative Artificial Intelligence' if code=='AI 2200' else None, 'human_context')
        c.update(source_id=CATALOG_SOURCE_ID, url=CATALOG_URL)
        courses.append(c)
    applications = []
    for p in section.find_all('p'):
        match = re.fullmatch(r'([A-Z]+ \d{4}) (.+)', clean(p))
        if match:
            c = course(*match.groups(), 'applications')
            c.update(source_id=CATALOG_SOURCE_ID, url=CATALOG_URL)
            courses.append(c)
            applications.append(c['id'])
    if len(applications) != 9:
        raise ValueError('Catalog application pool changed')
    for suffix, title, kind, count, ids in (
        ('catalog-core','Catalog: required foundations','all',None,[c['id'] for c in courses[:2]]),
        ('catalog-ethics','Catalog: ethics and responsible use','choose_courses',1,['vanderbilt-'+c.lower().replace(' ','-') for c in ethics]),
        ('catalog-applications','Catalog: AI applications and evaluation','choose_courses',1,applications)):
        r=requirement(suffix,title,kind,'2026–27 catalog requirement.',ids)
        r.update(source_id=CATALOG_SOURCE_ID,count=count,credits=6 if suffix.endswith('core') else 3)
        requirements.append(r)
    r=requirement('catalog-total','Catalog total: 12 hours','note','The 2026–27 catalog specifies 12 hours. The university credit definition identifies hours as semester hours.')
    r.update(source_id=CATALOG_SOURCE_ID,credits=12)
    requirements.append(r)
    return dict(id=PROGRAM_ID,title='Generative Artificial Intelligence',award_level='minor',program_kind='minor',curriculum_status='partial',courses=courses,requirements=requirements)


def parse_credit_definition(html: str) -> dict:
    text=clean(BeautifulSoup(html,'html.parser'))
    if 'Credit hours are semester hours' not in text or 'CREDIT HOUR DEFINITION' not in text:
        raise ValueError('Vanderbilt credit definition missing')
    return {'credit_unit':'semester_hours'}
