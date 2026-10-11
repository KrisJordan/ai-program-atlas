"""Literal-title classification can coexist with unresolved metadata identity."""
from pathlib import Path
import json
from urllib.parse import urldefrag
ROWS=json.loads(Path(__file__).with_name('reviewed_hass_holds.json').read_text())
URLS={urldefrag(r['url'])[0] for r in ROWS.values()}


def with_dispositions(parser,url):
    def wrapped(html):
        out=parser(html)
        for c in out.get('courses',[]):
            r=ROWS.get(c['id'])
            if r is None or urldefrag(r['url'])[0]!=urldefrag(url)[0]:continue
            # The source-specific parser still validates actual headings and rules.
            # A changed printed identity cannot inherit this prior title judgment.
            c['category']='other'
            if c.get('code')==r['code']and c.get('name')==r['name']:
                c['category']=r['category']
                c['notes']=list(dict.fromkeys(c.get('notes',[])+r['notes']))
        return out
    return wrapped
