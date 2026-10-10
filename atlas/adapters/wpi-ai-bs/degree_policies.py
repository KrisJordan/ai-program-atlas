"""Observed university rules shared by WPI bachelor degrees.

Every paraphrase is gated by its own source clause, not just a page title.
Unknown wording triggers review; parsers never issue a completeness audit.
"""

from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import requirement, text, course

BASE = "https://wpi.cleancatalog.net/"
# key: (path, exact heading, [(stable key,title,verifiable clause,summary,credits)])
POLICIES = {
    "degree": (
        "wpi-degree-requirements",
        "WPI Degree Requirements",
        [
            (
                "total",
                "Minimum academic credit",
                "minimum academic credit required for the Bachelor degree is 15 units",
                "Earn at least 15 academic units; use free electives beyond published distribution requirements to reach the minimum.",
                15,
            ),
            (
                "residence",
                "Residence",
                "minimum of eight units",
                "At least eight units must be completed satisfactorily in residence at WPI.",
                8,
            ),
            (
                "hua",
                "Humanities and arts",
                "two units of work in the humanities and arts",
                "Two units with the applicable humanities/arts sequence and completion evaluation.",
                2,
            ),
            (
                "science-total",
                "Mathematics and science baseline",
                "specific requirement is two units",
                "Two units in science, engineering, mathematics or computing, subject to the program’s stricter distribution.",
                2,
            ),
            (
                "quantitative",
                "Quantitative science baseline",
                "Two-thirds units of work must be in Quantitative Science",
                "At least 2/3 unit in quantitative science; eligible subjects are determined by the major.",
                2 / 3,
            ),
            (
                "natural",
                "Natural or engineering science baseline",
                "two-thirds units of work must be in Natural or Engineering Science",
                "At least 2/3 unit in natural or engineering science; the major determines eligible subjects.",
                2 / 3,
            ),
            (
                "flex-science",
                "Remaining science baseline",
                "final two-thirds unit may be",
                "The remaining 2/3 unit may be quantitative, natural or engineering science.",
                2 / 3,
            ),
            (
                "iqp",
                "Interactive Qualifying Project",
                "Interactive Qualifying Project, or IQP",
                "At least one unit of an approved project relating science/technology to society, with required documentation.",
                1,
            ),
            (
                "mqp",
                "Major Qualifying Project",
                "Major Qualifying Project, or MQP",
                "At least one unit of an approved project in the major, with required documentation. This includes rather than adds to the program MQP.",
                1,
            ),
            (
                "distribution",
                "Program distribution certification",
                "certified by the appropriate Program Review Committee",
                "Complete the major’s published distribution; certification is by its Program Review Committee on adviser recommendation.",
                None,
            ),
            (
                "social",
                "Social sciences",
                "2/3 unit of work in the social sciences, exclusive of qualifying project",
                "At least 2/3 social-science unit, excluding qualifying-project work.",
                2 / 3,
            ),
            (
                "wellness",
                "Wellness and physical education",
                "1/3 unit of course work (four WPE classes)",
                "Complete 1/3 WPE unit (normally four classes) or an approved equivalent.",
                1 / 3,
            ),
        ],
    ),
    "humanities": (
        "humanities-and-arts-requirement",
        "Humanities and Arts Requirement",
        [
            (
                "sequence",
                "Standard humanities sequence",
                "five student-selected courses followed by a 1/3 unit Inquiry Seminar or Practicum",
                "Complete five HUA courses before HU3900/HU3910 or an equivalent 1/3-unit inquiry seminar/practicum; submit the completion form afterward.",
                2,
            ),
            (
                "depth",
                "Thematic depth",
                "at least three courses of thematically-related work",
                "Before the capstone, take at least three related courses in AR, MU, TH, EN/WR/RH, HI/HU/INTL, PY/RE, or a faculty-approved interdisciplinary theme.",
                None,
            ),
            (
                "level",
                "Depth level",
                "at least one of the three thematically-related courses",
                "At least one depth course preceding the capstone must be at 2000 level or above. A 3000-level course is encouraged, not required.",
                None,
            ),
            (
                "breadth",
                "Breadth outside depth area",
                "at least one course outside the grouping",
                "Before the capstone, take a course outside the depth grouping. Groups: AR/TH/MU; SP/GN/ISE/AB/CN; EN/WR/RH; HI/HU/INTL; PY/RE. Six-course modern-language sequences are exempt.",
                None,
            ),
            (
                "language",
                "Language alternatives",
                "one of the following three ways",
                "Language paths: a practicum as the sixth language course; an advanced seminar after five language courses; or advanced-placement language competence with a mixed approved sequence ending in an advanced seminar.",
                None,
            ),
            (
                "ise",
                "Non-native English path",
                "3000-level or above ISE/WR project-based course",
                "Non-native English speakers may combine ISE/WR work and conclude with a project-based ISE/WR course at 3000 level or above.",
                None,
            ),
            (
                "practicum",
                "Practicum permission",
                "permission of the instructor is required",
                "Instructor permission is required for the practicum.",
                None,
            ),
            (
                "ap",
                "Advanced placement ceiling",
                "maximum of 1/3 unit of AP credit",
                "At most 1/3 AP unit counts toward HUA. German/Spanish scores 4–5 qualify subject to the starting-course restriction; studio art requires portfolio review. Additional AP credit may satisfy other requirements.",
                1 / 3,
            ),
            (
                "transfer",
                "Transfer completion alternatives",
                "fewer than six Humanities and Arts courses",
                "Transfers with fewer than six HUA courses complete the remaining two-unit sequence including a capstone. Two units completed before entry may satisfy HUA through coordinator approval of the completion form.",
                None,
            ),
            (
                "transfer-grade",
                "Transfer-credit evaluation",
                "grade of B- or better",
                "The general HUA rule accepts accredited US courses at B- or better; non-US work is individually reviewed. Prior approval is required after matriculation. The language subsection also retains legacy B/C thresholds and recommends B-; obtain coordinator determination for that conflict.",
                None,
            ),
            (
                "language-transfer",
                "Prior language study",
                "three or more years of modern-language study in high school",
                "Without AP, three years of high-school language may yield 1/3 transfer unit after two WPI courses at intermediate level or above. AP/high-school pathways require starting WPI language study at Elementary II or above.",
                None,
            ),
            (
                "offcampus",
                "Off-campus humanities alternative",
                "at least three courses on campus with one term",
                "An approved HUA project-center term may combine with at least three prior HUA courses/equivalents. HUA admission, required forms, adviser-directed preparation, written report and any required presentation apply; normally finish within one term under HUA faculty supervision.",
                None,
            ),
        ],
    ),
    "social": (
        "the-social-science-requirement",
        "The Social Science Requirement",
        [
            (
                "pool",
                "Eligible social sciences",
                "ECON, ENV, DEV, GOV, PSY, SD, SOC, SS, STS",
                "Two SSPS courses qualify: ECON, ENV, DEV, GOV, PSY, SD, SOC, SS or STS. SS/ID2050 qualifies. A 1/3-unit Great Problems Seminar may qualify only with a co-teacher holding at least a half-time SSPS appointment.",
                None,
            ),
            (
                "exclusions",
                "Social science exclusions",
                "CS 3043/SS 3043, IMGD 2000",
                "HUA, Business School and STEM social-implications courses do not qualify; CS3043/SS3043, IMGD2000 and EDU4100 are specifically excluded.",
                None,
            ),
            (
                "overlap",
                "Social-science overlap",
                "may overlap with the distribution requirements of any major",
                "Eligible social-science courses may also satisfy major distribution requirements.",
                None,
            ),
        ],
    ),
    "wellness": (
        "wellness-and-physical-education-requirement",
        "Wellness and Physical Education Requirement",
        [
            (
                "options",
                "Wellness alternatives and approval",
                "We do not offer independent study",
                "Repeated WPE courses may earn credit; independent study is unavailable. Approved varsity/club participation requires advance registration (varsity instructor permission); approved off-campus courses require advance approval. No retroactive credit. Some ROTC participation qualifies after commander review.",
                None,
            ),
        ],
    ),
    "iqp": (
        "the-interactive-qualifying-project",
        "The Interactive Qualifying Project",
        [
            (
                "preparation",
                "IQP preparation",
                "expected to complete a course devoted to project preparation",
                "Global Projects Program IQPs require a preparation course before travel. Projects may be on or off campus; reports are archived in Digital WPI.",
                None,
            ),
        ],
    ),
    "mqp": (
        "the-major-qualifying-project",
        "The Major Qualifying Project",
        [
            (
                "scope",
                "MQP disciplinary context",
                "application of the skills, methods, and knowledge of the discipline",
                "The MQP applies disciplinary knowledge to a representative professional problem, selected with the adviser to complement the overall program. A preliminary proposal is encouraged, not universally required.",
                None,
            ),
        ],
    ),
    "grading": (
        "grading-policies",
        "Grading Policies",
        [
            (
                "credit",
                "Credit-bearing completion",
                "credit has not been earned",
                "A/B/C are undergraduate course grades that earn credit; NR does not. IQP/MQP/HUA require an overall completion evaluation; project SP is temporary and must be replaced by a permanent grade.",
                None,
            ),
            (
                "gpa",
                "No institutional undergraduate GPA",
                "does not maintain a Cumulative Grade Point Average",
                "WPI does not maintain an undergraduate cumulative GPA. A numerical equivalent may be requested for external use; no GPA graduation threshold is inferred.",
                None,
            ),
        ],
    ),
    "major": (
        "designation-of-major-area-of-study",
        "Designation of Major Area of Study",
        [
            (
                "certification",
                "Major certification",
                "Program Review Committee (PRC)",
                "The appropriate program review committee certifies the major using the completed distribution and MQP, in consultation with the student and adviser.",
                None,
            ),
        ],
    ),
    "double-major": (
        "double-major",
        "Double Major",
        [
            (
                "requirements",
                "Optional double-major rules",
                "one unit in each of the two major areas of study",
                "Complete both distributions and one MQP unit in each major plus one IQP unit (three project units). Appropriate shared academic work may satisfy both majors; program-review approvals apply.",
                None,
            ),
        ],
    ),
    "graduate": (
        "graduate-courses",
        "Graduate Courses",
        [
            (
                "conversion",
                "Graduate-course use and conversion",
                "1 graduate credit = 1/6 undergraduate unit",
                "Graduate enrollment ordinarily does not require graduate admission; Business School courses require admission to a dual BS/MS program. The published conversion is one graduate credit to 1/6 undergraduate unit, processed by the Registrar.",
                None,
            ),
        ],
    ),
    "combined": (
        "combined-bachelormasters-program",
        "Combined Bachelor/Master’s Program",
        [
            (
                "approval",
                "Optional combined-degree approval",
                "Course Selection Form",
                "Shared BS/MS coursework requires adviser/graduate-coordinator planning and an approved course-selection agreement submitted to the Registrar. The agreement never waives either degree’s requirements.",
                None,
            ),
            (
                "sharing",
                "Optional BS/MS shared-credit limit",
                "No more than 40%",
                "Shared credit cannot exceed 40% of the master degree’s required credits; some departments limit it to 30%. The chosen graduate program and approved agreement determine the actual allowance.",
                None,
            ),
        ],
    ),
}

POLICIES.update(
    {
        "options": (
            "degree-options",
            "Degree Options",
            [
                (
                    "concentration",
                    "Concentration declaration and scope",
                    "two units of integrated academic study plus an MQP",
                    "A concentration requires two integrated-study units and a related MQP. Plan with the adviser and apply to the program review committee by its deadlines; concentration requirements cannot prevent completion of the major.",
                    None,
                ),
                (
                    "overlap",
                    "Additional-designation overlap ceiling",
                    "must not overlap with credit earned for another additional degree designation by more than one unit",
                    "Concentrations/minors may overlap another additional designation by at most one unit. No credit-bearing activity may be triple-counted across degree requirements or designations.",
                    None,
                ),
                (
                    "double-limit",
                    "Double-major eligibility",
                    "No student shall complete more than two undergraduate majors",
                    "At most two undergraduate majors; both programs must permit the combination. Exceptions to prohibited combinations need Committee on Academic Operations approval.",
                    None,
                ),
                (
                    "joint-mqp",
                    "Interdisciplinary double-major MQP alternative",
                    "One interdisciplinary project of at least 4/3 units",
                    "With advance signed approval, a 4/3-unit interdisciplinary MQP may satisfy both majors instead of two one-unit MQPs. It must cover both fields and be advised by faculty associated with both. Both program audits require certification; HUA is unchanged.",
                    None,
                ),
                (
                    "social-mqp",
                    "Social-science double-major exception",
                    "a single project bearing at least one unit credit",
                    "A social-science MQP may also satisfy IQP when an approved one-unit project meets both sets of goals. An interdisciplinary double-major MQP cannot also be the IQP.",
                    None,
                ),
            ],
        ),
        "graduation": (
            "graduation",
            "Graduation",
            [
                (
                    "application",
                    "Degree application deadline",
                    "May – prior A-term",
                    "Apply to the Registrar for May graduation during the preceding A term; for September or December graduation during the preceding D term.",
                    None,
                ),
            ],
        ),
        "transfer": (
            "transfer-credits",
            "Transfer Credits",
            [
                (
                    "evaluation",
                    "Transfer-credit approval",
                    "only those courses in which the student received a grade of C or better",
                    "Departments evaluate comparable accredited-institution courses individually. Normally C or better is considered; departments may require B- or higher. Vocational, correspondence, precollege/review, CEU, enrichment/refresher and CLEP work is excluded.",
                    None,
                ),
                (
                    "approval",
                    "Approval before outside study",
                    "before the course is taken",
                    "After matriculation, obtain department approval and its specified minimum grade on the transfer authorization form, file before study, then submit an official transcript. Consortium work may need separate distribution approval; otherwise it may be elective credit.",
                    None,
                ),
                (
                    "language",
                    "Retroactive language credit conditions",
                    "earning grades of B or higher in both courses",
                    "Without AP, retroactive language credit requires three high-school years averaging B, placement at least into term two, and two qualifying WPI terms graded B or better. Spanish specifically requires SP2521/2522. AP and high-school pathways cannot both earn credit.",
                    None,
                ),
                (
                    "math",
                    "Retroactive calculus credit conditions",
                    "no grades of NR in any course in the MA 1021-1024 sequence",
                    "Retroactive MA1021/1022 credit follows the specified sequential WPI calculus/MA2051 pathways. Both qualifying courses must pass on first attempt by D term of year one, with no first-year NR in MA1021–1024.",
                    None,
                ),
                (
                    "ap",
                    "AP and other prior-learning credit",
                    "complete list of AP credits for exams taken",
                    "AP/IB/PLTW awards depend on the applicable examination, score and department equivalency policy. They are credit-award alternatives, not a waiver of the degree distribution. HUA AP is capped at 1/3 unit.",
                    None,
                ),
            ],
        ),
        "projects": (
            "projects-and-research",
            "Projects and Research",
            [
                (
                    "approval",
                    "Project approval and registration",
                    "Projects must be accepted by a project advisor",
                    "An adviser must accept the project before registration. Register by the first term of work; no-penalty registration closes on term day ten. MQP supervision must include faculty associated with the major.",
                    None,
                ),
                (
                    "report",
                    "Project reporting",
                    "report must be prepared to the satisfaction of the project advisor",
                    "Meet adviser expectations for interim work and a satisfactory final report. Sponsor projects normally need written/oral reports; team documentation must identify individual contributions.",
                    None,
                ),
                (
                    "submission",
                    "Electronic project submission",
                    "minimum of 1/6 unit of qualifying project credit",
                    "Submit the final IQP/MQP as PDF electronically with adviser approval, normally one report per team; register for at least 1/6 project unit in the submission term.",
                    None,
                ),
                (
                    "completion",
                    "Degree-requirement completion recording",
                    "last Thursday in D-term",
                    "Completion forms are due by day ten of the following term; May candidates need the eCDR by the last Thursday of D term. After day ten, recording MQP/IQP/HUA completion requires at least 1/6 unit of that activity in the current term unless a written adviser petition is approved.",
                    None,
                ),
                (
                    "sponsor",
                    "Sponsor review and agreements",
                    "grade and final report cannot be submitted",
                    "Off-campus work requires proper registration and sponsor-agreement compliance. Submit sponsor copies early for confidentiality review (often 30 days); final grading/submission waits for that review.",
                    None,
                ),
                (
                    "overload",
                    "Global-project overload restriction",
                    "Students are not permitted to overload",
                    "No overload during a one-term off-campus Global Projects Program project or the preceding ID2050-plus-prequalifying-project term.",
                    None,
                ),
                (
                    "paid",
                    "Paid sponsored-project conditions",
                    "before the fifth day",
                    "Paid IQP/MQP work needs Undergraduate Studies approval before work: documented learning purpose, faculty control of assessment, and approved project agreement/scope. Submit by day five of the preceding term and remain registered during work; prior unregistered employment earns no project credit.",
                    None,
                ),
            ],
        ),
    }
)


def parse(html, pid, title, key):
    path, heading, rules = POLICIES[key]
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if not main or not main.find("h1") or text(main.find("h1")) != heading:
        raise ValueError("WPI policy heading changed")
    body = text(main)
    source = pid + "-policy-" + key
    requirements = []
    for rid, label, guard, summary, credits in rules:
        if guard not in body:
            raise ValueError("WPI policy clause changed: " + guard)
        requirements.append(
            requirement(
                pid,
                "policy-" + key + "-" + rid,
                label,
                source,
                kind="note",
                credits=credits,
                summary=summary,
                category="human_context"
                if key in ("humanities", "social", "wellness")
                else "other",
            )
        )
    if key == "options" and pid == "wpi-business-analytics-applied-ai-bs":
        import re

        listed = []
        for li in main.find_all("li"):
            value = text(li)
            if value.startswith("Business Analytics & Applied AI and "):
                listed.append(value.removeprefix("Business Analytics & Applied AI and "))
        if not listed:
            raise ValueError("Business double-major prohibitions missing")
        requirements.append(
            requirement(
                pid,
                "policy-options-business-prohibitions",
                "Disallowed business double majors",
                source,
                kind="note",
                summary="Cannot combine this degree with "
                + ", ".join(listed)
                + ", except with Committee on Academic Operations approval.",
            )
        )
    courses = []
    if key == "humanities":
        for code in ["HU 3900", "HU 3910"]:
            if code not in body:
                raise ValueError("Humanities capstone codes changed")
            courses.append(
                course(
                    code,
                    None,
                    source,
                    BASE + path,
                    credits=1 / 3,
                    institution="wpi",
                    category="human_context",
                )
            )
        requirements[0]["course_ids"] = [c["id"] for c in courses]
    return dict(
        id=pid,
        title=title,
        award_level="BS",
        program_kind="degree",
        catalog_year=None,
        curriculum_status="partial",
        courses=courses,
        requirements=requirements,
        notes=[
            "Observed university policy component. Applicable exceptions and degree-specific restrictions still require reconciliation."
        ],
    )


def attach(namespace, keys=None):
    for key in keys or POLICIES:
        url = BASE + POLICIES[key][0]
        if url not in namespace["SOURCES"]:
            namespace["SOURCES"].append(url)
        namespace["SOURCE_PARSERS"][url] = lambda html, key=key: parse(
            html, namespace["PROGRAM_ID"], namespace["TITLE"], key
        )
