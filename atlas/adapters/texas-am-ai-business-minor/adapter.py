"""Extract the five required business AI courses and all minor-specific policies."""
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import require_phrases,content,clean,course,rule,policy
PROGRAM_ID='texas-am-ai-business-minor'
SOURCES=('https://catalog.tamu.edu/undergraduate/business/artificial-intelligence-business-minor/',)
SOURCE_ID=PROGRAM_ID+'-identity'

def parse(html):
    root=content(html,'Artificial Intelligence in Business - Minor')
    require_phrases(root, ['completed 24 credit hours', 'at least 12 credit hours completed at Texas A&M University', 'not on the diploma'])
    table=root.find('table',class_='sc_courselist')
    if not table:raise ValueError('Minor course table absent')
    courses=[];total=None
    for row in table.find_all('tr'):
        cells=row.find_all('td',recursive=False)
        if 'listsum' in row.get('class',[]):total=int(clean(cells[-1].get_text()));continue
        if len(cells)!=3:continue
        a=cells[0].find('a',class_='code')
        if not a:continue
        c=course('tamu',clean(a.get_text(' ',strip=True)),clean(cells[1].get_text(' ',strip=True)),SOURCE_ID,urljoin(SOURCES[0],a['href']),credits=int(clean(cells[2].get_text())),unit='semester_hours',category='applications');courses.append(c)
    if not courses or total is None:raise ValueError('Required course or total missing')
    groups=[rule('tamu-business-ai-core','Required courses',SOURCE_ID,[c['id'] for c in courses],credits=total,unit='semester_hours',summary='Complete all listed courses, totaling the published15semester credit hours.')]
    for marker,gid,title,summary in [
      ('overall 2.0 GPA or better','completion','Completion GPA','Earn an overall GPA of at least2.0 in the minor courses.'),
      ('overall GPA of 3.00 or higher','eligibility','Enrollment eligibility','Overall GPA must be at least3.00; complete24credit hours, including at least12at Texas A&M.'),
      ('Declaration of the minor is made through','declaration','Declaration','Declare through the major college or department; students are encouraged to begin courses once declared.'),
      ('Once declared, minor requirements become graduation requirements','award','Graduation and recognition','A declared minor becomes a graduation requirement. It is recorded on the transcript after graduation, not on the diploma.'),
      ('Minimum of 6 hours at the 300-400 level','level','Upper-level minimum','At least6hours must be at the300–400level.')]:
      groups.append(policy(root,marker,'tamu-'+gid,title,summary,SOURCE_ID))
    return dict(id=PROGRAM_ID,title='Artificial Intelligence in Business',award_level='minor',program_kind='minor',courses=courses,requirements=groups)
