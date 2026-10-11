"""Hash-guarded observed metadata for the two reviewed business additional majors.

Manual category reviews live only in seeds. Changed descriptions drop editorial
summaries and categories, rather than recertifying an old source judgment.
"""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup


def clean(node):
    return ' '.join(node.get_text(' ', strip=True).split()) if node else ''


def extract(html, review):
    soup = BeautifulSoup(html, 'html.parser')
    code = review['code']
    if review['format'] == 'courseleaf':
        blocks = [b for b in soup.select('.courseblock') if clean(b.select_one('.detail-code')) == code]
        if len(blocks) != 1:
            raise ValueError('Course identity missing or duplicated: ' + code)
        block = blocks[0]
        title = clean(block.select_one('.detail-title'))
        desc = clean(block.select_one('.courseblockextra'))
        prereq = clean(block.select_one('.detail-prereq')).removeprefix('Prerequisite: ').strip() or None
        amount = clean(block.select_one('.detail-hours_html'))
        match = re.fullmatch(r'\((\d+(?:\.\d+)?) credits?\)', amount)
    else:
        blocks = [b for b in soup.select('.node__content') if any(clean(h).startswith(code + ':') for h in b.find_all(['h1','h3']))]
        if len(blocks) != 1:
            raise ValueError('Course identity missing or duplicated: ' + code)
        block = blocks[0]
        heading = next(h for h in block.find_all(['h1','h3']) if clean(h).startswith(code + ':'))
        title = clean(heading).split(':', 1)[1].strip()
        desc = clean(block.select_one('.field--name-field-description'))
        prereq = clean(block.select_one('.field--name-field-pr .field__item')) or None
        amount = clean(block.select_one('.field--name-field-credits .field__item'))
        match = re.fullmatch(r'(\d+(?:\.\d+)?)', amount)
    if not desc or not match:
        raise ValueError('Course description/credits missing: ' + code)
    return title, desc, prereq, float(match[1])


def parse_metadata(html, *, pid, url):
    rows=json.loads((Path(__file__).parent / pid / 'course_reviews.json').read_text())
    observations=[]; digests={}; changes=[]
    for review in rows:
        if review['url'] != url:
            continue
        title, desc, prereq, credits=extract(html,review)
        if title != review['source_title']:
            raise ValueError('Reviewed source title changed: ' + review['code'])
        digest=hashlib.sha256(desc.encode()).hexdigest()
        c={k:review[k] for k in ('id','code','name','source_id','url','credit_unit')}
        c.update(credits=credits,prerequisites=prereq,public_site=None,syllabus=None)
        if digest==review['description_sha256']:
            c.update(description=review['description'],category=review['category'])
            if review.get('notes'):
                c['notes']=review['notes']
        else:
            c.update(description=None,category='other');changes.append(review['code'])
        observations.append(c);digests[c['id']]=digest
    if not observations:
        raise ValueError('No registered course records for source')
    return dict(id=pid,courses=observations,requirements=[],curriculum_status='partial',
                observed_description_digests=digests,
                notes=['Observed exact source course metadata; independent category/completeness review is manual.']+
                      (['Changed descriptions require review: '+', '.join(changes)] if changes else []))


def register(pid, sources, parsers):
    rows=json.loads((Path(__file__).parent / pid / 'course_reviews.json').read_text())
    for url in dict.fromkeys(r['url'] for r in rows):
        if url not in sources:sources.append(url)
        parsers[url]=lambda html,url=url:parse_metadata(html,pid=pid,url=url)
