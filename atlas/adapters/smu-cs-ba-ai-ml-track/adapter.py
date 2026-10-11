"""Observed SMU local curriculum and linked course metadata."""
from atlas.adapters import national_depth_curricula as curricula

PROGRAM_ID = 'smu-cs-ba-ai-ml-track'
SOURCES = ('https://catalog.smu.edu/programs/CS-BA/requirements-krhha', curricula.SMU_CREDIT, *curricula.SMU_COURSE_URLS.values())

def parse(html):
    return curricula.parse_smu(html, 'smu-ba')

def parse_credit(html):
    return curricula.parse_smu_credit(html, 'smu-ba')

def parse_ai(html):
    return curricula.parse_smu_course(html, 'smu-ba', '0046401')

def parse_ml(html):
    return curricula.parse_smu_course(html, 'smu-ba', '0268171')

SOURCE_PARSERS = {curricula.SMU_CREDIT: parse_credit, curricula.SMU_COURSE_URLS['0046401']: parse_ai, curricula.SMU_COURSE_URLS['0268171']: parse_ml}
