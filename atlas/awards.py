"""Evidence-backed award filters, independent from hosting school or title guesses."""

BUCKETS = ("BS", "BSE", "BA", "other")


def validate_award_options(program):
    options = program.get("award_options", [])
    if not isinstance(options, list):
        raise ValueError("award_options must be a list")
    if options and program.get("program_kind") != "degree":
        raise ValueError("Award options describe standalone degree records only")
    sources = {source["id"] for source in program.get("sources", [])}
    seen = set()
    for option in options:
        if not isinstance(option, dict):
            raise ValueError("Award option must be an evidence-backed object")
        if option.get("normalized") not in BUCKETS:
            raise ValueError("Unknown normalized award option")
        if any(not isinstance(option.get(key), str) or not option[key].strip()
               for key in ("label", "source_id", "locator")):
            raise ValueError("Award option needs exact label, source and evidence locator")
        if option["source_id"] not in sources:
            raise ValueError("Award option references an unknown source")
        identity = option["label"], option["normalized"]
        if identity in seen:
            raise ValueError("Duplicate award option")
        seen.add(identity)


def major_award_buckets(program):
    """Return one or more verified buckets; never infer from host or text prefixes.

    Explicit second-major-only relationships have their own non-award bucket. Optional
    source-backed options support a genuinely combined degree record; separately
    cataloged BA/BS records retain their separate IDs and curricular inventories.
    """
    if program.get("major_relationship", {}).get("kind") == "second_major_only":
        from .program_relationships import validate_program_relationships
        validate_program_relationships(program)
        return ["second_major"]
    if program.get("program_kind") != "degree":
        return ["other"]
    if program.get("award_options"):
        validate_award_options(program)
        values = {option["normalized"] for option in program["award_options"]}
        return [bucket for bucket in BUCKETS if bucket in values]
    exact = program.get("award_level")
    return [exact if exact in BUCKETS else "other"]
