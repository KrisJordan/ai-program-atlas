"""Public concentration identity plus separately exported requirements text."""
from atlas.adapters import stanford_symsys_concentrations as sources
PROGRAM_ID = 'stanford-symsys-ai-concentration'
SOURCES = (sources.CONFIG['ai'][2],)
def parse(html): return sources.parse(html, 'ai')
def parse_document(text): return sources.parse_document(text, 'ai')
SOURCE_PARSERS = {SOURCES[0]: parse}
DOCUMENT_TEXT_PARSERS = {sources.CONFIG['ai'][3]: parse_document}

SOURCES += tuple(x[0] for x in sources.POLICIES.values()) + (sources.CORE,)
SOURCE_PARSERS.update({value[0]:(lambda html,key=key:sources.parse_policy(html, 'ai', key)) for key,value in sources.POLICIES.items()})
SOURCE_PARSERS[sources.CORE] = lambda html: sources.parse_core(html, 'ai')
