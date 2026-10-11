"""Public concentration identity plus separately exported requirements text."""
from atlas.adapters import stanford_symsys_concentrations as sources
PROGRAM_ID = 'stanford-symsys-hai-concentration'
SOURCES = (sources.CONFIG['hai'][2],)
def parse(html): return sources.parse(html, 'hai')
def parse_document(text): return sources.parse_document(text, 'hai')
SOURCE_PARSERS = {SOURCES[0]: parse}
DOCUMENT_TEXT_PARSERS = {sources.CONFIG['hai'][3]: parse_document}
