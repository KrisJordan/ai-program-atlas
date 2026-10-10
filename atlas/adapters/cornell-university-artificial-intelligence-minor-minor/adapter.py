"""Extract only the requirements visible on Cornell's accessible department page."""
import re
from atlas.adapters.national_curriculum_common import require_phrases,content,clean,rule,policy
PROGRAM_ID='cornell-university-artificial-intelligence-minor-minor'
SOURCES=('https://bowers.cornell.edu/programs/artificial-intelligence-minor',)
SOURCE_ID=PROGRAM_ID+'-official'

def parse(html):
    r=content(html,'AI minor');text=clean(r.get_text(' ',strip=True))
    require_phrases(r, ['INFO 3170', 'Human-AI Interaction', 'Ethics, Governance & Policy', 'forbidden overlaps'])
    m=re.search(r'at least (\w+) courses \((\d+) credits minimum\)',text)
    if not m or m[1]!='six':raise ValueError('Reviewed six-course minimum changed')
    groups=[rule('cornell-minimum','Minimum coursework',SOURCE_ID,kind='note',credits=int(m[2]),summary='At least six courses and 18 credits. Full foundation and elective distribution remains unextracted; this is not an unrestricted choose-six pool.')]
    for marker,gid,title,summary in [
      ('letter grade of "C" or higher','grades','Grade requirement','Every course must receive a letter grade of C or better.'),
      ('open to all undergraduate students','eligibility','Eligibility','Open to all undergraduate students.'),
      ('MAE 3200','updates','Published course approvals','MAE 3200 also satisfies the Machine Learning foundation category; INFO 3170 is an approved elective. Course metadata and the full pool remain unverified.'),
      ('if NOT used towards the foundations requirement','reuse','Foundation/elective reuse','Human-AI Interaction and Ethics, Governance & Policy foundation courses may serve as electives only when not used for a foundation requirement; forbidden overlap rules also apply and require catalog review.'),
      ('last semester as an undergraduate','application','Application timing','Apply after completing all required courses at C or better, or in the final undergraduate semester while enrolled in the remaining courses.')]:
      groups.append(policy(r,marker,'cornell-'+gid,title,summary,SOURCE_ID))
    return dict(id=PROGRAM_ID,title='Artificial Intelligence',award_level='minor',program_kind='minor',requirements=groups,
                notes=['Detailed linked catalog returned a JavaScript robot challenge. No bypass attempted. Only accessible department requirements observed; curriculum remains partial.'])
