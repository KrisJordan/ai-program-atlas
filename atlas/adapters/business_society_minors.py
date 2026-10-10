"""Observed curriculum candidates; reviewer audits and policies remain curated."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def clean(value):
    return " ".join(value.split())


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def course(code, name, pid, sid, url, credits=None, unit="unknown"):
    return dict(id=pid+"-"+slug(code), code=code, name=name, description=None,
        prerequisites=None, credits=credits, credit_unit=unit, category="other",
        source_id=sid, url=url, public_site=None, syllabus=None)


def requirement(pid, key, title, sid, ids, kind="all", count=None, credits=None, unit="unknown", summary=None):
    return dict(id=pid+"-"+key, parent_id=None, title=title, kind=kind, count=count,
        credits=credits, credit_unit=unit, category="other", source_id=sid,
        source_text=None, summary=summary or title, course_ids=ids)


def observe(html, pid, title, sid, url, style):
    soup=BeautifulSoup(html,"html.parser")
    headings=[clean(h.get_text(" ",strip=True)) for h in soup.find_all("h1")]
    if title not in headings and title+" Minor" not in headings and "Minor in "+title not in headings:
        raise ValueError("Program heading missing or changed")
    if style == "miami" and "Minor in "+title not in headings:
        raise ValueError("Minor award heading missing")
    if style == "rit" and title+" Minor" not in headings:
        raise ValueError("Minor award heading missing")
    courses=[]; requirements=[]
    if style.startswith("nd"):
        core=[]; electives=[]
        for block in soup.find_all(class_="accordion"):
            button=block.find("button")
            text=clean(block.get_text(" ",strip=True))
            match=re.search(r"Course Number: ([A-Z]+ \d{5}(?: / \d{5})?) Credit Hours: ([0-9.]+)",text)
            if not match:
                continue
            name=clean(button.get_text(" ",strip=True))
            name=re.sub(r"^[A-Z]+ - ","",name)
            c=course(match[1],name,pid,sid,url,float(match[2]))
            courses.append(c)
            previous=block.find_previous("h3")
            (electives if previous and "Electives" in previous.get_text() else core).append(c["id"])
        for h in soup.find_all("h3"):
            if "Electives" not in h.get_text(): continue
            ul=h.parent.find("ul")
            if ul:
                for li in ul.find_all("li",recursive=False):
                    m=re.fullmatch(r"([A-Z]+ \d{5}):? (.+)",clean(li.get_text(" ",strip=True)))
                    if not m: raise ValueError("Elective format changed")
                    c=course(m[1],m[2],pid,sid,url)
                    if c["id"] not in [x["id"] for x in courses]:
                        courses.append(c);electives.append(c["id"])
        text=clean(soup.get_text(" ",strip=True))
        m=re.search(r"must take at least ([0-9.]+) CH",text)
        if not core or not electives or not m: raise ValueError("Required or elective inventory missing")
        requirements=[requirement(pid,"core","Core courses",sid,core),
            requirement(pid,"electives","Approved electives",sid,electives,"note",credits=float(m[1]),summary="Choose at least "+m[1]+" published credit hours from this pool; normalized credit unit is unverified.")]
    else:
        table=soup.find("table",class_="sc_courselist")
        if not table: raise ValueError("Curriculum table missing")
        current=None; groups=[]
        unit="semester_hours" if "semester credit hours" in soup.get_text() else "unknown"
        numbers={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
        for row in table.find_all("tr"):
            cells=row.find_all("td",recursive=False)
            if not cells: continue
            link=row.find("a",class_="code")
            text=clean(row.get_text(" ",strip=True))
            hours=cells[-1].get_text(strip=True)
            credit=float(hours) if re.fullmatch(r"[0-9.]+",hours) else None
            if link:
                if current is None: raise ValueError("Course precedes requirement group")
                code=clean(link.get_text(" ",strip=True))
                name=clean(cells[1].get_text(" ",strip=True))
                name=re.sub(r" \d+$","",name)
                c=course(code,name,pid,sid,urljoin(url,link.get("href","")),credit,unit)
                courses.append(c);current["course_ids"].append(c["id"])
                continue
            if "Total" in text: continue
            m=re.search(r"Select (one|two|three|four|five|six|seven|eight|nine|ten)",text)
            if text.startswith("Select ") and not m:
                raise ValueError("Unrecognized selection rule")
            if m:
                current=requirement(pid,"choice-"+str(len(groups)),clean(cells[0].get_text(" ",strip=True)),sid,[],"choose_courses",numbers[m[1]],credit,unit)
                groups.append(current)
            elif "Prerequisite course" in text or "Required Course" in text:
                current=requirement(pid,"prerequisite" if "Prerequisite" in text else "core",clean(cells[0].get_text(" ",strip=True)),sid,[],"choose_courses" if "Prerequisite" in text else "all",1 if "Prerequisite" in text else None,credit,unit)
                groups.append(current)
        requirements=[g for g in groups if g["course_ids"]]
        if not courses or not requirements: raise ValueError("Empty curriculum")
    return dict(id=pid,title=title,award_level="minor",program_kind="minor",curriculum_status="partial",courses=courses,requirements=requirements)
