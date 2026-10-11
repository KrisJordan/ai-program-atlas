"""Manual title judgments for a bounded architecture source subset.

This reads actual requirement pages/PDF text; it never replays seed courses or
certifies the saved review. Exact source digests retain version/annotation scope.
"""
import hashlib
import json
from importlib import import_module
from pathlib import Path

PKG = 'atlas.adapters.mit-ai-decision-making-bs.'
FIELDS = import_module(PKG + 'hass_fields')
ARCH = import_module(PKG + 'hass_architecture')
CMSW = import_module(PKG + 'hass_cmsw')
MANIFEST = json.loads(Path(__file__).with_name('reviewed_architecture_remainder.json').read_text())


def source_parse(url, text):
    for key, (_, pdf_url) in ARCH.PDFS.items():
        if url == pdf_url:
            return ARCH.parse_pdf_text(key, text)
    for module in [FIELDS, ARCH, CMSW]:
        if url in module.SOURCE_PARSERS:
            return module.SOURCE_PARSERS[url](text)
    raise ValueError('Unregistered architecture source')


def parse(text, url):
    return enrich(source_parse(url, text), text, url)


def enrich(result, text, url):
    digest = hashlib.sha256(text.encode()).hexdigest()
    for c in result.get('courses', []):
        saved = MANIFEST['courses'].get(c['id'])
        if saved is None:
            continue
        c['category'] = 'other'
        if (saved['source_digest'] == digest and saved['source_url'] == url
                and (saved['code'], saved['name'], saved['source_id']) ==
                (c['code'], c['name'], c['source_id'])):
            c['category'] = saved['category']
            c['notes'] = list(dict.fromkeys(c.get('notes', []) + saved['notes']))
    result['observed_architecture_source_digest'] = digest
    return result


SOURCE_PARSERS = {url: (lambda text, url=url: parse(text, url))
                  for url in MANIFEST['sources']}


def with_reviews(primary, url):
    return lambda text: enrich(primary(text), text, url)
