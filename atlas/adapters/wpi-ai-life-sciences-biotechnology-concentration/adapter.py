from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-life-sciences-biotechnology-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-life-sciences-and-0',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Life Sciences and Biotechnology', SOURCES[0])
