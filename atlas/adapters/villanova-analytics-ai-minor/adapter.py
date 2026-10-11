"""Observed Villanova local curriculum; completeness is reviewer-only."""

from atlas.adapters.villanova_curriculum import parse_program

PROGRAM_ID = "villanova-analytics-ai-minor"
SOURCES = [
    "https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-minor",
    "https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html",
    "https://live-villanova-catalog.cleancatalog.io/",
]


def parse(html: str) -> dict:
    return parse_program(
        html,
        pid=PROGRAM_ID,
        title="Analytics & Artificial Intelligence",
        award="minor",
        kind="minor",
        url=SOURCES[0],
    )


from atlas.adapters.villanova_curriculum import parse_course

SOURCE_PARSERS = {SOURCES[0]: parse}
SOURCES.append("https://live-villanova-catalog.cleancatalog.io/management/mgt-3170")
SOURCE_PARSERS["https://live-villanova-catalog.cleancatalog.io/management/mgt-3170"] = lambda html: (
    parse_course(
        html,
        pid=PROGRAM_ID,
        code="MGT 3170",
        url="https://live-villanova-catalog.cleancatalog.io/management/mgt-3170",
    )
)
SOURCES.append("https://live-villanova-catalog.cleancatalog.io/management/mgt-4170")
SOURCE_PARSERS["https://live-villanova-catalog.cleancatalog.io/management/mgt-4170"] = lambda html: (
    parse_course(
        html,
        pid=PROGRAM_ID,
        code="MGT 4170",
        url="https://live-villanova-catalog.cleancatalog.io/management/mgt-4170",
    )
)


# Bounded metadata review: observations do not certify a curriculum audit.
from functools import partial as _metadata_partial
from atlas.adapters.small_complete_metadata_batch2 import CONFIG as _metadata_config, parse_metadata as _parse_metadata

SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
for _key in ['villanova-eco-3137', 'villanova-fin-2360', 'villanova-mgt-3180', 'villanova-mgt-3600', 'villanova-mis-2030', 'villanova-mis-3050', 'villanova-mis-3060', 'villanova-mkt-2240']:
    _cfg = _metadata_config[_key]
    if _cfg["url"] not in SOURCES:
        SOURCES = list(SOURCES) + [_cfg["url"]]
    SOURCE_PARSERS[_cfg["url"]] = _metadata_partial(_parse_metadata, key=_key)

from atlas.adapters.small_complete_metadata_batch2 import parse_aim as _parse_aim

_previous_identity_parser = SOURCE_PARSERS.get('https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-minor')
def _parse_identity_with_aim(html):
    observed = _previous_identity_parser(html) if _previous_identity_parser else {"id": PROGRAM_ID}
    observed.update(_parse_aim(html, 'villanova'))
    return observed
if 'https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-minor' not in SOURCES:
    SOURCES = list(SOURCES) + ['https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-minor']
SOURCE_PARSERS['https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-minor'] = _parse_identity_with_aim
