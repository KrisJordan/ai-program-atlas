"""Guarded observations for separately reviewed Miami Judaic/Latin American/urban chapters.

Manual taxonomy judgments stay in the manifest; parsers do not certify audits.
"""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import clean, course

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())


def parse(html, *, pid, key):
    wanted = {c:e for c,e in SPEC['courses'].items() if e['key']==key and pid in e['program_ids']}
    if key not in SPEC['sources'] or not wanted:
        raise ValueError('Unreviewed Miami Judaic/Latin American/urban source/program scope')
    source=SPEC['sources'][key]
    soup=BeautifulSoup(html,'html.parser');heading=soup.find('h1')
    if not heading or clean(heading.get_text(' ',strip=True))!=source['heading']:
        raise ValueError('Miami Judaic/Latin American/urban chapter identity changed')
    inventory=sorted(clean(t.get_text(' ',strip=True)).split('.')[0] for t in soup.select('.courseblock .courseblocktitle'))
    missing={c:e for c,e in SPEC['missing_courses'].items() if e['key']==key and pid in e['program_ids']}
    if set(inventory)&missing.keys():
        raise ValueError('Previously missing course now appears; review required')
    if hashlib.sha256('\n'.join(inventory).encode()).hexdigest()!=source['course_code_inventory_hash']:
        raise ValueError('Miami Judaic/Latin American/urban inventory changed; review required')
    records=[];ranges={};seen=set()
    for block in soup.select('.courseblock'):
        title=block.select_one('.courseblocktitle')
        if title is None:continue
        label=clean(title.get_text(' ',strip=True));code=label.split('.')[0]
        if code not in wanted:continue
        if code in seen:raise ValueError('Duplicate reviewed Miami identity')
        seen.add(code);entry=wanted[code]
        if hashlib.sha256(clean(block.get_text(' ',strip=True)).encode()).hexdigest()!=entry['block_hash']:
            raise ValueError('Miami Judaic/Latin American/urban course changed; review required: '+code)
        match=re.fullmatch(r'([A-Z]+ \d+)\. (.*?)\. (\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?) Credit Hours?\.',label)
        if not match or match[2]!=entry['name']:raise ValueError('Miami Judaic/Latin American/urban identity/amount changed')
        amount=None if '-' in match[3] else float(match[3])
        record=course(code,match[2],pid,'miami-context-courses-'+key,source['url'],amount,unit=entry['credit_unit'])
        record.update(description=entry['description'],prerequisites=entry['prerequisites'],category=entry['category'])
        records.append(record)
        if amount is None:
            lo,hi=map(float,match[3].split('-'));ranges[code]={'minimum':lo,'maximum':hi,'credit_unit':entry['credit_unit']}
    if seen!=set(wanted):raise ValueError('Missing reviewed Miami Judaic/Latin American/urban identities')
    return {'id':pid,'courses':records,'observed_credit_ranges':ranges,
            'observed_missing_courses':{c:{'source_url':source['url'],'scope':'No exact block in this inspected chapter'} for c in missing}}


def _compose(previous,html,*,pid,key):
    old=previous(html);new=parse(html,pid=pid,key=key);records=old.get('courses',[])
    if old.get('id')!=pid or len({c['id'] for c in records})!=len(records):raise ValueError('Invalid prior observations')
    merged={c['id']:c for c in records}
    for record in new['courses']:
        before=merged.get(record['id'])
        if before and before['code']!=record['code']:raise ValueError('Conflicting Miami identity')
        merged[record['id']]={**(before or {}),**record}
    return {**old,'courses':list(merged.values()),'observed_credit_ranges':{**old.get('observed_credit_ranges',{}),**new['observed_credit_ranges']},
            'observed_missing_courses':{**old.get('observed_missing_courses',{}),**new['observed_missing_courses']}}


def register(pid,sources,parsers):
    keys={e['key'] for e in SPEC['courses'].values() if pid in e['program_ids']}
    if not keys:raise ValueError('Unreviewed Miami Judaic/Latin American/urban program scope')
    for key in sorted(keys):
        url=SPEC['sources'][key]['url']
        if url not in sources:sources.append(url)
        previous=parsers.get(url)
        if getattr(previous,'_miami_judaic_latin_urban_context',None)==pid:continue
        callback=partial(_compose,previous,pid=pid,key=key) if previous else partial(parse,pid=pid,key=key)
        callback._miami_judaic_latin_urban_context=pid
        parsers[url]=callback
