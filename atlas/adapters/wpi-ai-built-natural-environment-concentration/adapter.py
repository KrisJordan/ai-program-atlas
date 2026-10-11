from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-built-natural-environment-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-built-and-natural',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Built and Natural Environment', SOURCES[0])
