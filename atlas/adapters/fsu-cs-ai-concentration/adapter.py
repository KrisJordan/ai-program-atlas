"""Source-specific local curriculum candidates; manual audit remains partial."""
from atlas.adapters import national_depth_curricula as curricula

PROGRAM_ID = 'fsu-cs-ai-concentration'
SOURCES = ('https://www.cs.fsu.edu/academics/undergraduate-programs/artificial-intelligence-concentration/',)

def parse(html):
    return curricula.parse_fsu(html)

# PDF_TEXT_PARSER requires reviewed text extraction and visual inspection; the
# generic HTTP refresh intentionally does not pretend PDF bytes are HTML.
PDF_TEXT_PARSER = curricula.parse_fsu_flowchart_text
