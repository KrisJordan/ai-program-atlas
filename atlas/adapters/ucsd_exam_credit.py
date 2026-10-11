"""Observed current exam-credit tables, conditional on score, subject and college."""
import re
from atlas.adapters.cmu_bs.common import text, slug
from atlas.adapters.ucsd_college_context import requirement
from atlas.adapters.ucsd_degree_policies import PID,guarded
from atlas.adapters.ucsd_revelle_pools import section
AP_URL='https://catalog.ucsd.edu/_files/advanced-placement-credit-chart-2026.pdf'
IB_URL='https://catalog.ucsd.edu/_files/international-baccalaureate-credits-chart-2026.pdf'
WARREN_URL='https://warren.ucsd.edu/academics/general-education/ap-ib-credit.html'
COLLEGES=['Revelle','Muir','Marshall','Warren','Roosevelt','Sixth','Seventh','Eighth']


def node(key,title,source,summary,parent=None):
    return requirement(PID,'exam-'+key,title,PID+'-exam-'+source,unit='quarter_hours',category='other',kind='note',parent=parent,summary=summary)


def clean(value):
    return re.sub(r'\s+',' ',value or '').strip()


def parse_pdf_observation(rows,kind):
    """Input is reviewer-checked ten-column PDF rows, never an HTML shell."""
    if kind not in ['ap','ib']or not rows:raise ValueError('Unknown exam chart or empty observation')
    result=[]
    for i,row in enumerate(rows):
        cells=row.get('cells',[]);page=row.get('page')
        if len(cells)!=10 or not all(isinstance(x,str)and x.strip()for x in cells)or not isinstance(page,int)or page<1:raise ValueError('Exam table columns or page changed')
        cells=[clean(x)for x in cells];label=cells[0].split('*',1)[0].strip();key=kind+'-'+str(i)
        root=node(key,label,kind,'2026–27 '+kind.upper()+' chart, PDF page'+str(page)+'. Exam/unit/duplicate-subject condition: '+cells[0]+'. University course exemption or placement: '+cells[1]+'. Values are exam credit or exemption conditions, not credits assigned to an inferred course; amounts omitted by the source remain unknown.');result.append(root)
        for j,college in enumerate(COLLEGES):
            result.append(node(key+'-'+slug(college),college+' treatment — '+label,kind,'Conditional '+college+' exam-credit treatment in the 2026–27 chart: '+cells[j+2]+'. Apply only the student’s college and qualifying score/subject; do not add mutually exclusive college allowances together.',root['id']))
    if kind=='ap':
        policy='AP usually requires3or higher, subject to specific rows. Duplicate AP/IB subject or college-course content earns credit only once; exempt/equivalent UCSD courses cannot be retaken for credit. AP credit does not force earlier major declaration or graduation. AP Precalculus has no units (4/5may support placement); Seminar/Research may meet ELWR without units. African American Studies has no unit amount printed in the PDF first column, so no amount is inferred from that chart.'
    else:
        policy='Higher Level scores5or higher normally earn8quarter units; Standard Level does not earn units, but EnglishA score6/7meets ELWR. IB diploma score30or higher earns6quarter units. Duplicate examination/course content earns credit once; follow explicit row exceptions such as the partial IB History of Americas/APUSHistory overlap. Mathematics Applications and Interpretations is explicitly not credit-eligible; Analysis and Approaches has its distinct row. Unlisted exams require advising.'
    result.append(node(kind+'-policy',kind.upper()+' general exam-credit qualifications',kind,policy))
    return dict(id=PID,curriculum_status='partial',requirements=result)


def parse_warren(html):
    s=section(html,'Advanced Placement and International Baccalaureate Credit');v=text(s)
    guarded(v,['2026-2027 Academic Year','4 units to each AS','IB credit limit at UC San Diego is 30 units','The IB Math AI HL is not UC transferable'])
    result=[node('warren-policy','Warren exam credit applicability','warren','The page is explicitly2026–27; exam-year exemptions may differ. Area Studies accepts at most4exam units per area; the page also describes PofC allowances for other degree routes, which are not AI’s engineering Area Study requirements. IB total-credit limit is30units. Exempt courses cannot earn duplicate credit. The page’s IBMath table says MATH20A plus4elective units while its following note and the university chart say MATH20A and10B; preserve the discrepancy.')]
    tables=s.find_all('table')
    if not tables:raise ValueError('No Warren exam tables')
    for i,t in enumerate(tables):
        heading=t.find_previous('h2');kind=text(heading)if heading else None
        if kind not in ['Advanced Placement Credit','International Baccalaureate Credit']:raise ValueError('Exam family boundary changed')
        subject=None;n=0
        for tr in t.find_all('tr'):
            cells=[text(c)for c in tr.find_all(['th','td'])]
            if not any(cells):continue
            if len(cells)==4 and cells[1:3]==['Score','Units']:subject=cells[0];continue
            if subject is None:raise ValueError('Exam subject header missing')
            if len(cells)not in [1,3,4]:raise ValueError('Warren exam row shape changed')
            label='Footnote'if len(cells)==1 else'Qualification row'
            result.append(node('warren-'+str(i)+'-'+str(n),kind+' — '+subject+' '+label,'warren','Observed '+label.lower()+' for '+subject+': '+' | '.join(cells)+'. Columns retain the printed subtest, score/exemption, units and college-use qualifications; blank cells do not imply unrestricted eligibility. PofC-only allowances are not engineering Area Study waivers.'));n+=1
        if not n:raise ValueError('Empty Warren exam table')
    return dict(id=PID,curriculum_status='partial',requirements=result)
