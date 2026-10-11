"""Rice AI major table observations; external university rules remain a review gap."""
from bs4 import BeautifulSoup
from atlas.adapters.rice_degree_courses import classify_observed
from atlas.adapters.national_curriculum_common import content,clean,require_phrases
from atlas.adapters.degree_table_observations import Tables, reviewed_outcomes


def parse_rice(html,pid,url):
    root=content(html,'Bachelor of Science (BS) Degree with a Major in Artificial Intelligence')
    for sup in root.find_all('sup'):sup.decompose()
    require_phrases(root,['A minimum of 20-21 courses (67-69 credit hours)','A minimum of 120 credit hours','A minimum of 10 courses (33 credit hours)','A maximum of 5 courses (20 credit hours)','A minimum major GPA of 2.00','Select 1 course (3-4 credit hours) from 3 of the following 5','Official Certifier'])
    tables=root.find_all('table',class_='sc_courselist')
    if len(tables)!=2:raise ValueError('Rice major table structure changed')
    t=Tables('rice-ai',pid+'-catalog',url)
    rows=tables[1].find_all('tr');core=[];domains={};domain=None;electives=False
    names=['Artificial Intelligence Theory','Cognitive Psychology','Knowledge and Graphs','Perception and Language','Robotics and Autonomy']
    for row in rows:
        text=clean(row.get_text(' ',strip=True))
        if text.startswith('Elective Requirements'):electives=True;continue
        if not electives:core.append(str(row));continue
        if text in names:domain=text;domains[domain]=[];continue
        if domain and row.find('td',class_='codecol'):domains[domain].append(str(row))
    if list(domains)!=names:raise ValueError('Rice elective domains changed')
    t.table(BeautifulSoup('<table>'+''.join(core)+'</table>','html.parser').table,'Required mathematics, computing and AI courses')
    choice=t.group('Choose three of five elective areas',kind='choose_courses',count=3,summary='Choose three distinct areas. In each chosen area take one course carrying 3–4 credit hours; the three electives total 9–11 credit hours.')
    for name,items in domains.items():
        t.table(BeautifulSoup('<table>'+''.join(items)+'</table>','html.parser').table,name,parent=choice['id'],kind='alternative',interpret_choices=False)
    t.group('Major and degree totals',kind='note',summary='The major requires 20–21 courses and 67–69 credit hours, including at least 10 courses and 33 credit hours at level 300 or above. The degree requires at least 120 credit hours. Course choices determine the ranges.')
    t.group('Major GPA and transfer limits',kind='note',summary='Major coursework requires a GPA of at least 2.00. After matriculation, at most five courses and 20 credit hours of transfer or study abroad credit may apply to specific major requirements; departmental equivalency approval is required.')
    t.group('Course substitutions',kind='note',summary='Unlisted substitutions require the major advisor or applicable director of undergraduate studies to approve them and the official certifier to record them in Degree Works.')
    outcomes=reviewed_outcomes(root,'Program Learning Outcomes for the BS Degree with a Major in Artificial Intelligence',[
        (['mathematical concepts','artificial intelligence problems'],'Use calculus, linear algebra, probability and statistics to solve AI problems.'),
        (['Design and implement','algorithms and models'],'Build AI algorithms and models for complex computational tasks.'),
        (['performance and limitations','metrics and testing'],'Assess AI performance and limitations through suitable metrics and tests.'),
        (['ethical implications','responsible AI'],'Incorporate ethical analysis and responsible AI practices into development.')],pid+'-catalog')
    return dict(outcomes=outcomes,id=pid,title='Artificial Intelligence',award_level='BS',program_kind='degree',courses=classify_observed(list(t.courses.values())),requirements=t.rules)
