"""Observed local concentration rules; host AI degree is separately audited."""
from atlas.adapters import wpi_local_concentrations as local
PROGRAM_ID = 'wpi-ai-business-applications-concentration'
KEY = 'business'

def parse(html):
    return local.parse(html, PROGRAM_ID, KEY)

local.attach(globals(), KEY)
