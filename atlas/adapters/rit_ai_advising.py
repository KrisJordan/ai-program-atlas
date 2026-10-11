"""Reviewed public 2026–27 advising PDF; catalog conflicts stay explicit."""
import hashlib
from atlas.adapters.national_curriculum_common import clean, course, rule
PROGRAM_ID='rochester-institute-of-technology-artificial-intelligence-bs-degree'
URL='https://www.rit.edu/computing/sites/rit.edu.computing/files/docs/IST-Information/AI%202026_0.pdf'
SOURCES=[URL]
SID='rit-ai-bs-advising-2026-2027'
REVIEWED_HASH='daa6230835cce4912ecebd22758dbad7e8c3a239115ba5ce9cfd43f3f514e30e'
ELECTIVES=[('CSCI-431','Introduction to Computer Vision'),('EEEE-485','Robotic Systems'),('CSCI-632','Mobile Robot Programming'),('LING-582','Natural Language Processing II'),('LING-584','Undergraduate Speech Processing'),('SWEN-566','AI Centric Software'),('PUBL-550','AI, Policy and Law')]


def parse_reviewed(text):
    """Text extracted from a visually reviewed two-page PDF, never PDF bytes/HTML."""
    if hashlib.sha256(clean(text).encode()).hexdigest()!=REVIEWED_HASH:
        raise ValueError('RIT advising PDF changed or unavailable; visual review required')
    courses=[course(PROGRAM_ID,code,name,SID,URL,3,'semester_hours',category='electives') for code,name in ELECTIVES]
    capstone_id=PROGRAM_ID+'-idai-490'
    requirements=[
        rule(PROGRAM_ID+'-advising-wi','Program writing-intensive designation',SID,[capstone_id],kind='note',summary='The 2026–27 School of Information flowchart explicitly marks IDAI-490 AI Team Capstone as WI-PR and requires fourth-year standing. It separately shows first-year writing and an additional Writing Intensive checkbox; these fit the existing university three-course structure, not extra credits.'),
        rule(PROGRAM_ID+'-advising-elective-conflict','Advising elective list differs from catalog',SID,[c['id'] for c in courses],kind='note',summary='The 2026–27 advising PDF says to select two three-credit AI electives. It lists CSCI-431; EEEE-485 OR CSCI-632; LING-582; LING-584; SWEN-566; PUBL-550. The separately captured catalog instead uses CSCI-634 for robotics and omits the two linguistics options. These source-specific options are retained as conflicting evidence, not combined into one approved pool.'),
        rule(PROGRAM_ID+'-advising-immersion','Independent advising chart and immersion ambiguity',SID,kind='note',summary='The 2026–27 flowchart shows three separate immersion slots and labels MATH-190 as discrete mathematics, without an immersion designation. It therefore does not establish an exception to the university no-program-overlap rule or resolve the captured catalog’s extra Immersion 3 annotation.')]
    return dict(id=PROGRAM_ID,courses=courses,requirements=requirements)
