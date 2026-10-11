"""Public concentration identity plus separately exported requirements text."""
from atlas.adapters import stanford_symsys_concentrations as sources
PROGRAM_ID = 'stanford-symsys-ai-concentration'
SOURCES = (sources.CONFIG['ai'][2],)
def parse(html): return sources.parse(html, 'ai')
def parse_document(text): return sources.parse_document(text, 'ai')
SOURCE_PARSERS = {SOURCES[0]: parse}
DOCUMENT_TEXT_PARSERS = {sources.CONFIG['ai'][3]: parse_document}
