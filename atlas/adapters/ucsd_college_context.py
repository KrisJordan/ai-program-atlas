"""Keep source-specific UCSD college pathways outside the universal major tree.

The existing catalog pathway notes establish enrollment-dependent applicability.
Cohort, certification and optional-route details stay in the observed rules; this
module does not choose a college or turn those conditions into elective loads.
"""
from atlas.adapters.cmu_bs.common import requirement as make_requirement

PID = "university-of-california-san-diego-artificial-intelligence-bs-degree"
COLLEGE_SOURCE_PREFIXES = {
    "revelle-college": ("revelle-", "transfer-options-humanities", "transfer-options-revelle"),
    "john-muir-college": ("muir-",),
    "thurgood-marshall-college": ("marshall-", "transfer-options-marshall", "closure-marshall-language"),
    "earl-warren-college": ("warren-", "exam-warren"),
    "eleanor-roosevelt-college": ("roosevelt-",),
    "sixth-college": ("sixth-",),
    "seventh-college": ("seventh-",),
    "eighth-college": ("eighth-",),
}


def college_parent(source_id):
    """Match only registered UCSD college-source namespaces, never course titles."""
    if not source_id.startswith(PID + "-"):
        return None
    local = source_id[len(PID) + 1:]
    for college, prefixes in COLLEGE_SOURCE_PREFIXES.items():
        if local.startswith(prefixes):
            return PID + "-policy-college-" + college
    return None


def requirement(*args, **kwargs):
    """Create the observed rule while preserving existing within-source nesting."""
    row = make_requirement(*args, **kwargs)
    if row["parent_id"] is None:
        row["parent_id"] = college_parent(row["source_id"])
    return row
