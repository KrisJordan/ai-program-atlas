"""Optional Global Languages HASS criteria; offerings are not closed pools."""
import re
from functools import partial
from importlib import import_module
from atlas.adapters.national_curriculum_common import content, clean, course, rule, require_phrases
optional = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments').optional
wrapped = import_module('atlas.adapters.mit-ai-decision-making-bs.hass_open_fields').wrapped
PID = 'mit-ai-decision-making-bs'
PROGRAMS = 'https://languages.mit.edu/academic-programs/'
PLACEMENT = 'https://languages.mit.edu/language-placement-proficiency/'
TRANSFER = 'https://languages.mit.edu/transfer-credit/'
LANGUAGES = ['Chinese', 'French', 'German', 'Japanese', 'Korean', 'Portuguese', 'Russian', 'Spanish', 'Other Languages']


def parse_programs(html):
    root = content(html, 'Academic Programs')
    h = root.find(lambda n:n.name == 'h2' and clean(n.get_text(' ',strip=True)) == 'HASS Concentrations')
    if h is None: raise ValueError('Language concentration section missing')
    nodes=[h]
    for n in h.find_next_siblings():
        if n.name == 'h2':break
        nodes.append(n)
    pane=wrapped(nodes)
    require_phrases(pane, ['consult with the relevant advisor', 'submit the HASS Concentration Form', 'Chinese, French, German, Japanese, Korean, Portuguese, Russian, Spanish, Other Languages', 'advance at least through semester “IV”', 'minimum of three subjects', 'commence at semester I should typically complete four subjects', 'commence at semester II or above need only three subjects', 'With advisor approval, other subject combinations', 'two subjects at semester IV or higher in different languages', 'plus one linguistic theory subject', 'three, twelve-unit subjects', 'coherent theme or area of focus', 'selected in consultation with the SILC advisor', 'appropriate transfer credit examiner and the Concentration advisor', 'another accredited institution'])
    sid=PID+'-hass-language-programs';rules=[]
    for name in LANGUAGES:
        prefix='mit-ai-hass-language-'+name.lower().replace(' ','-')
        rules.append(optional(prefix,name,sid))
        routes=prefix+'-routes'
        rules.append(rule(routes,'Placement-dependent language progression',sid,parent=prefix,kind='alternative',summary='Complete the applicable typical route or another combination approved by the concentration advisor. Progress must reach semester IV or higher and include at least three subjects.'))
        rules.append(rule(prefix+'-beginner','Typical semester-I start: four subjects',sid,parent=routes,kind='choose_courses',count=4,summary='A student beginning at semester I typically completes semesters I–IV. These are language-progression levels, not four academic terms of residence.'))
        rules.append(rule(prefix+'-higher','Semester-II-or-higher start: three subjects',sid,parent=routes,kind='choose_courses',count=3,summary='A student beginning at semester II or higher needs three subjects, progressing through at least semester IV; examples are II–IV or III–V. Advisor-approved combinations may differ, but the stated minimum/progression conditions remain.'))
        rules.append(rule(prefix+'-approval','Advisor declaration and approved external coursework',sid,parent=prefix,kind='note',summary='Consult the relevant advisor and submit the HASS concentration form. Other Languages includes Latin, Classical Greek and Old English at MIT; Harvard/Wellesley cross-registration and other accredited-institution coursework are possible. The latter requires both transfer-credit examiner and concentration-advisor approval. These are open language/level criteria, not an absent finite elective list.'))
    prefix='mit-ai-hass-language-theory'
    rules += [optional(prefix,'Theory of Language',sid),rule(prefix+'-advanced','Two advanced subjects in different languages',sid,parent=prefix,kind='choose_courses',count=2,summary='Complete two language subjects at semester IV or higher, in different languages.'),rule(prefix+'-theory','One linguistic theory subject',sid,parent=prefix,kind='choose_courses',count=1,summary='Complete one linguistic theory subject in addition to the two advanced language subjects; consult the concentration advisor and submit the HASS form.')]
    prefix='mit-ai-hass-language-silc'
    rules += [optional(prefix,'Studies in International Literatures and Cultures',sid),rule(prefix+'-three','Three twelve-unit subjects with a coherent focus',sid,parent=prefix,kind='choose_courses',count=3,summary='Choose three twelve-unit SILC subjects, taught in English, sharing a coherent theme or area of focus, with the SILC advisor. Foreign-language study is not a prerequisite imposed by this concentration. Submit the HASS concentration form.')]
    return dict(id=PID,requirements=rules)


def parse_placement(html):
    root=content(html,'Language Placement & Proficiency')
    require_phrases(root,['For placement in “Regular Track” subjects','For placement in “Streamlined Track” subjects','one year of French in high school','one semester at the college level','two years of French in high school','two semesters at the college level','three years of French in high school','three semesters at the college level','Scores of 4 or 5 on the French AP exam','A placement test is required for students who have not taken a prerequisite course at MIT','Students who have not taken Spanish at MIT are required to take a Spanish placement test','brief written evaluation and an oral assessment','heritage speaker of Spanish'])
    sid=PID+'-hass-language-placement';prefix='mit-ai-hass-language-placement';cs=[]
    french=root.find(lambda n:n.name=='h3' and clean(n.get_text())=='French')
    nodes=[]
    for n in french.find_next_siblings():
        if n.name=='h3':break
        nodes.append(n)
    text=clean(wrapped(nodes).get_text(' ',strip=True))
    for code in dict.fromkeys(re.findall(r'21G\.\d+',text)):
        name=re.search(re.escape(code)+r' (French I{1,3}V?|French IV)',text)
        cs.append(course(prefix,code,name[1] if name else None,sid,PLACEMENT,unit='units',category='human_context'))
    if not cs:raise ValueError('French placement course observations missing')
    return dict(id=PID,courses=cs,requirements=[
        rule(prefix,'Language placement context',sid,kind='note',summary='Placement determines the appropriate starting level for the optional language concentration, not earned academic credit. Contact the designated language staff for Chinese regular/streamlined tracks, German, Korean, Portuguese or Russian. Graduate-language and English-evaluation tests on this page are not undergraduate HASS concentration requirements.'),
        rule(prefix+'-french','French prior-study and AP placement',sid,[c['id'] for c in cs],parent=prefix,kind='note',summary='One high-school year or college semester places into 21G.302 (French II); two into 21G.303 (III); three into 21G.304 (IV). French AP 4/5 indicates readiness for the five named advanced subjects, not course credit or an automatic concentration waiver.'),
        rule(prefix+'-japanese','Japanese placement test',sid,parent=prefix,kind='note',summary='A placement test is required when the prerequisite course has not been taken at MIT. Submit the placement form to obtain a level recommendation.'),
        rule(prefix+'-spanish','Spanish placement assessment',sid,parent=prefix,kind='note',summary='Students who have not taken Spanish at MIT must take written and oral placement assessments. The usual window is the two weeks before classes; other times may be arranged. The contact route differs for one–two, three, or four-plus prior years/AP experience and heritage speakers; uncertain students use the general placement contact. No placement category awards credit by itself.')])


def parse_transfer(html):
    root=content(html,'Transfer Credit')
    require_phrases(root,['strongly encouraged','preliminary review','confirm if a minimum grade may be required','All final decisions','related to the academic foci of residential 21G subjects','type of credit (HASS or elective)','SHASS Dean’s Office','An official transcript must be submitted directly','AY2024','Harvard University, Wellesley College, and Massachusetts College of Art','Transfer credit processes are not required'])
    sid=PID+'-hass-language-transfer'
    return dict(id=PID,requirements=[rule('mit-ai-hass-language-transfer','External Global Languages coursework and documentation',sid,kind='note',summary='Contact the appropriate examiner before outside coursework for a strongly encouraged preliminary review, including any applicable minimum grade. Final credit depends on completed-course evidence and relevance to residential 21G subject matter; merely being taught in a language is insufficient. The examiner determines HASS/elective classification and amount after reviewing catalog/instructor/institution information, syllabus/assignments, grade report and work samples. Signed HASS requests go to the SHASS Dean’s Office and the official transcript to the registrar. Harvard/Wellesley/MassArt cross-registration does not use the transfer-credit process. The contact roster is labeled AY2024 and is not asserted to be current. The program page separately requires concentration-advisor approval for applicable outside coursework.')])


FIELD_SPECS={
 'chinese':('Chinese Studies',16,['declared minors, declared concentrators, first-years, sophomores, juniors, seniors and graduate students','attend the first day of class'], 'Chinese I–VI, regular and streamlined tracks, are capped at 16. Preregistration preference includes undergraduates previously cut for capacity and requires first-day attendance; priority then runs minors, concentrators, first-years, sophomores, juniors, seniors, graduate students.'),
 'french':('French & Francophone Studies',18,['declared majors, declared minors, declared concentrators','attend the first day of class'], 'Enrollment is capped at 18. Preregistration preference includes undergraduates previously cut for capacity and requires first-day attendance. Priority then runs majors, minors, concentrators, first-years, sophomores, juniors, seniors, graduate students.'),
 'german':('German Studies',18,['declared majors, declared minors, declared concentrators','attend the first day of class'], 'Enrollment is capped at 18. Preregistration preference includes undergraduates previously cut for capacity and requires first-day attendance. The general priority order is majors, minors, concentrators, first-years, sophomores, juniors, seniors, graduate students.'),
 'japanese':('Japanese Studies',16,['sophomores, first-years, juniors, seniors and graduate students','Within each category, priority will be given to pre-registered students'], 'Enrollment is capped at 16. Priority runs sophomores, first-years, juniors, seniors, graduate students, with preregistration preference within each category. This page does not state the majors-first order used by several other languages.'),
 'korean':('Korean Studies',16,['declared concentrators, first-years, sophomores, juniors, seniors and graduate students','attend the first day of class','No listeners'], 'Enrollment is capped at 16 with no listeners. Preregistration preference includes undergraduates previously cut for capacity and requires first-day attendance; priority runs concentrators, first-years, sophomores, juniors, seniors, graduate students.'),
 'portuguese':('Portuguese Studies',18,['declared concentrators, first-years, sophomores, juniors, seniors and graduate students'], 'Enrollment is capped at 18. Preregistration preference includes undergraduates previously cut for capacity; priority runs concentrators, first-years, sophomores, juniors, seniors, graduate students. No first-day-attendance condition is added from other language pages.'),
 'russian':('Russian Studies',None,[], 'The page directs the Russian concentration to the central Academic Programs requirements and placement guidance. It publishes no general enrollment-cap rule in the reviewed content.'),
 'spanish':('Spanish Studies',18,['declared majors, declared minors, declared concentrators','attend the first day of class'], 'Enrollment is capped at 18. Preregistration preference includes undergraduates previously cut for capacity and requires first-day attendance; priority runs majors, minors, concentrators, first-years, sophomores, juniors, seniors, graduate students.'),
}


def parse_field(key,html):
    title,cap,markers,summary=FIELD_SPECS[key]
    root=content(html,title)
    if not root.find('a',href=PROGRAMS):raise ValueError('Language academic-program reference missing')
    require_phrases(root,['Concentration','placement information']+markers)
    if cap is not None:require_phrases(root,['Enrollment limited to '+str(cap),'pre-registered students'])
    sid=PID+'-hass-language-'+key+'-context'
    return dict(id=PID,requirements=[rule('mit-ai-hass-language-'+key+'-enrollment','Published '+key.title()+' enrollment context',sid,parent='mit-ai-hass-language-'+key,kind='note',summary=summary+' These are enrollment conditions, not a guarantee of a seat or a different concentration subject count. Seasonal offerings on the page are not treated as a closed eligibility list.')])


SOURCE_PARSERS={PROGRAMS:parse_programs,PLACEMENT:parse_placement,TRANSFER:parse_transfer}
SOURCE_PARSERS.update({'https://languages.mit.edu/areas-of-study/'+key+'-studies/':partial(parse_field,key) for key in FIELD_SPECS})

OTHER = 'https://languages.mit.edu/areas-of-study/theory-of-languages-and-other-languages/'
SILC = 'https://languages.mit.edu/areas-of-study/studies-in-international-literatures-cultures/'


def parse_other_context(html):
    root=content(html,'Theory of Languages and Other Languages')
    require_phrases(root,['second language acquisition and bilingualism','See Academic Programs','languages other than those offered in Global Languages','Harvard University and Wellesley College','Latin, Classical Greek, and Old English'])
    if not root.find('a',href=PROGRAMS):raise ValueError('Other Languages program reference missing')
    sid=PID+'-hass-language-other-theory-context'
    return dict(id=PID,requirements=[rule('mit-ai-hass-language-other-context','Other Languages scope and shared requirements',sid,parent='mit-ai-hass-language-other-languages',kind='note',summary='This field page explicitly directs its requirements to Academic Programs and permits languages outside Global Languages through Harvard/Wellesley cross-registration or Latin, Classical Greek and Old English in MIT Literature. It does not publish a separate numerical requirement.'),rule('mit-ai-hass-language-theory-context','Theory of Languages scope and shared requirements',sid,parent='mit-ai-hass-language-theory',kind='note',summary='This page links the Theory of Languages concentration to the central Academic Programs criteria. Its stated focus connects linguistic perspectives on second-language acquisition/bilingualism with advanced language study; it does not add a separate required subject pool.')])


def parse_silc_context(html):
    root=content(html,'Studies in International Literatures & Cultures')
    require_phrases(root,['subjects are taught in English','regardless of foreign language proficiency','Academic Programs'])
    if not root.find('a',href=PROGRAMS):raise ValueError('SILC program reference missing')
    sid=PID+'-hass-language-silc-context'
    return dict(id=PID,requirements=[rule('mit-ai-hass-language-silc-context','SILC English-language instruction and proficiency scope',sid,parent='mit-ai-hass-language-silc',kind='note',summary='The field page explicitly says its subjects are taught in English and are appropriate regardless of foreign-language proficiency. It directs concentration requirements to Academic Programs. Its seasonal offerings are examples of available study, not an exhaustive approved concentration pool.')])


SOURCE_PARSERS.update({OTHER:parse_other_context,SILC:parse_silc_context})
