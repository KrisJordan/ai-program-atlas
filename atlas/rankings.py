"""Select a cited, edition-specific numerical rank without combining cohorts."""

from urllib.parse import urlparse

NUMERIC_STATUSES = {"primary_verified", "enumerated_secondary", "secondary_reported"}


def institution_rank_context(institution, category, edition=None):
    """Return a sortable rank and separate original evidence for its display.

    A cited secondary enumeration can supply ordering while remaining visibly
    secondary. An inferred edition, a membership bound, unknown provenance or
    conflicting values cannot supply a sortable rank. Missing ranks stay null.
    With no target edition, only one explicit recorded edition is unambiguous.
    """
    rows = [dict(row) for row in institution.get("rankings", [])
            if row.get("publisher") == "U.S. News" and row.get("category") == category]
    target = str(edition) if edition is not None else None
    if target is None:
        editions = {str(row["edition"]) for row in rows if row.get("edition")}
        target = next(iter(editions)) if len(editions) == 1 else None
    matching = [row for row in rows if target is not None
                and str(row.get("edition")) == target]

    def valid(row):
        rank = row.get("rank")
        return (type(rank) is int and rank > 0
                and row.get("verification_status") in NUMERIC_STATUSES
                and urlparse(row.get("source_url") or "").scheme in {"http", "https"})

    eligible = [row for row in matching if valid(row)]
    values = {row["rank"] for row in eligible}
    # Prefer primary evidence for display, never a smaller convenient rank.
    def evidence_order(row):
        return (row.get("verification_status") != "primary_verified",
                str(row.get("source_url") or ""), str(row.get("rank")))

    evidence = sorted(eligible or matching or rows, key=evidence_order)
    chosen = evidence[0] if evidence else {}
    rank = next(iter(values)) if len(values) == 1 else None
    if rank is not None:
        reason = "verified_primary" if chosen.get("verification_status") == "primary_verified" else "cited_secondary"
    elif len(values) > 1:
        reason = "conflicting_ranks"
    elif rows and (not matching or chosen.get("verification_status") == "primary_edition_inferred"):
        reason = "edition_unverified"
    elif chosen.get("rank") is None:
        reason = "rank_unknown"
    else:
        reason = "rank_unverified"
    return {
        "rank": rank,
        "reported_rank": chosen.get("rank"),
        "edition": chosen.get("edition") or target,
        "category": category,
        "source_url": chosen.get("source_url"),
        "verification_status": chosen.get("verification_status"),
        "reason": reason,
    }


def program_rank_key(program, institution, category, edition=None):
    """Alphabetical order within a rank does not alter the published tied rank."""
    rank = institution_rank_context(institution, category, edition)["rank"]
    return (rank is None, rank if rank is not None else 0,
            institution.get("name", "").casefold(), program.get("title", "").casefold(),
            program.get("id", ""))
