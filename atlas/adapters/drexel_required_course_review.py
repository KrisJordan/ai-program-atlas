"""Read exact Drexel prescribed-course result blocks; no seed or review replay."""
import hashlib
import json
import re
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import clean
PID='drexel-ai-ml-bs'
SPEC=json.loads(Path(__file__).with_suffix('.json').read_text())

def parse(html,code):
 soup=BeautifulSoup(html,'html.parser');entry=SPEC[code]
 result=next((r for r in soup.select('article.search-courseresult') if r.h3 and clean(r.h3.get_text(' ',strip=True)).startswith(code+' ')),None)
 if result is None:raise ValueError('Drexel exact course result missing: '+code)
 if hashlib.sha256(clean(result.get_text(' ',strip=True)).encode()).hexdigest()!=entry['digest']:
  raise ValueError('Drexel reviewed course result changed: '+code)
 title=clean(result.h3.get_text(' ',strip=True));match=re.fullmatch(re.escape(code)+r' (.+) (\d+(?:\.\d+)?) Credits?',title)
 if not match:raise ValueError('Drexel course title/credit header changed')
 block=result.select_one('.courseblock');value=clean(block.get_text(' ',strip=True))
 clauses=[]
 for label in ['Restrictions','Prerequisites','Corequisites']:
  found=re.search(label+r': (.*?)(?= (?:Restrictions|Prerequisites|Corequisites):|$)',value)
  if found:clauses.append(label+': '+found[1])
 return {'id':PID,'courses':[dict(id=entry['id'],code=code,name=match[1],description=entry['description'],prerequisites='; '.join(clauses) or None,credits=float(match[2]),credit_unit='unknown',category=entry['category'],source_id=entry['source_id'],url=entry['url'])]}

def register(sources,parsers):
 for code,entry in SPEC.items():
  sources.append(entry['url']);parsers[entry['url']]=partial(parse,code=code)
