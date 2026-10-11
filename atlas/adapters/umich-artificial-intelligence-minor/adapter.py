"""Engineering news confirms a distinct minor; it does not supply a curriculum."""
from atlas.adapters.national_curriculum_common import content,require_phrases,rule
PROGRAM_ID='umich-artificial-intelligence-minor'
URL='https://news.engin.umich.edu/2025/11/new-ai-minor-launches-for-students-across-disciplines/'
SID='umich-cse-ai-minor-news'
SOURCES=(URL,)


def parse(html):
    root=content(html,'New AI minor launches for students across disciplines')
    require_phrases(root,[
        'In Winter 2026, University of Michigan Engineering established a new minor in artificial intelligence',
        'skills to build custom AI solutions tailored to their disciplines',
        'Students majoring in engineering, information, music, pharmacy, business, art & design, and architecture can currently enroll',
        'sophomore in biomedical engineering who is pursuing the AI minor',
    ])
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',
        outcomes=[dict(text='Develop skills to construct AI solutions for the student’s discipline.',kind='source_stated',statement_type='program_aim',source_id=SID,locator='Opening paragraph; program aim, not an assessed learning outcome')],
        requirements=[rule('umich-cse-ai-minor-news-eligibility','College eligibility reported in the Engineering news article',SID,kind='note',summary='The updated report names engineering, information, music, pharmacy, business, art/design and architecture students as able to enroll. This dated news statement is not a complete current declaration policy; other colleges are not inferred eligible or ineligible.')])
