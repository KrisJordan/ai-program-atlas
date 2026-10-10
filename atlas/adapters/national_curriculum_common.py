"""Small constructors for reviewed national-minor source observations."""
import hashlib
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def clean(value):
    return ' '.join(value.split())


def content(html, identity):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('input', attrs={'type':'password'}) or any(
        re.search(r'^(log ?in|sign in|access denied|just a moment|javascript is disabled)', n.get_text(' ',strip=True),re.I)
        for n in soup.find_all(['title','h1'])):
        raise ValueError('Access page is not curriculum evidence')
    root = soup.find('main') or soup.find(id='content') or soup
    for n in root.find_all(['nav','aside','footer','script','style']): n.decompose()
    if identity.casefold() not in clean(root.get_text(' ',strip=True)).casefold():
        raise ValueError('Expected program identity missing')
    return root


def course(prefix, code, name, sid, url, credits=None, unit='unknown', category='other', topic=None):
    cid = prefix+'-'+re.sub('[^a-z0-9]+','-',code.casefold()).strip('-')
    if topic: cid+='-'+hashlib.sha256(topic.encode()).hexdigest()[:8]
    return dict(id=cid,code=code,name=name,description=None,prerequisites=None,credits=credits,
                credit_unit=unit,category=category,source_id=sid,url=url,public_site=None,syllabus=None)


def rule(gid, title, sid, ids=(), *, parent=None, kind='all', count=None, credits=None, unit='unknown', summary=None, category='other'):
    return dict(id=gid,parent_id=parent,title=title,kind=kind,count=count,credits=credits,credit_unit=unit,
                category=category,source_id=sid,source_text=None,summary=summary or title,course_ids=list(ids))


def policy(root, marker, gid, title, summary, sid):
    if marker.casefold() not in clean(root.get_text(' ',strip=True)).casefold():
        raise ValueError('Reviewed policy changed: '+marker)
    return rule(gid,title,sid,kind='note',summary=summary)
