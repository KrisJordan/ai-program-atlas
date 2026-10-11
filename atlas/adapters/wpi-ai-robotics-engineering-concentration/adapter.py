from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-robotics-engineering-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-robotics-engineering',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Robotics Engineering', SOURCES[0])
