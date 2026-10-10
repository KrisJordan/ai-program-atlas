"""Evidence-backed requirement inheritance without merging award identities."""

from copy import deepcopy
import re

from .requirements import validate_requirements

CLASSIFICATIONS = {"source_stated", "analyst_classified", "unknown"}
COMPONENTS = {"ai_core", "domain", "integration", "other"}
RELATIONSHIPS = {"ai_plus_x", "x_plus_ai", "integrated", "unknown"}


def validate_family(family):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", family.get("id", "")):
        raise ValueError("Family ID must be a safe slug")
    if not family.get("institution_id") or not family.get("name"):
        raise ValueError("Family needs an institution and name")
    if family.get("classification_kind") not in CLASSIFICATIONS - {"unknown"}:
        raise ValueError("Family grouping needs an explicit classification basis")
    sources = family.get("sources", [])
    source_ids = {s["id"] for s in sources}
    if not sources or len(source_ids) != len(sources):
        raise ValueError("Family needs unique evidence sources")
    for source in sources:
        if not source.get("url", "").startswith(("https://", "http://")):
            raise ValueError("Family source needs an HTTP(S) URL")
    shared = family.get("shared_requirements", [])
    if not shared:
        raise ValueError("Family needs a reviewed shared requirement inventory")
    course_codes = set()
    requirements = []
    for node in shared:
        if node.get("source_id") not in source_ids:
            raise ValueError("Shared requirement needs registered family evidence")
        if node.get("component", "other") not in COMPONENTS:
            raise ValueError("Unknown family component")
        codes = node.get("course_codes", [])
        if not isinstance(codes, list) or any(not isinstance(c, str) or not c for c in codes):
            raise ValueError("Shared requirement course codes must be strings")
        course_codes.update(codes)
        requirements.append({**node, "course_ids": codes})
    validate_requirements(
        {"courses": [{"id": code} for code in course_codes], "requirements": requirements}
    )


def resolve_program(program, family=None):
    """Expand live definitions for reading; never mutate or silently promote a seed."""
    result = deepcopy(program)
    membership = result.get("family")
    if not membership:
        return result
    if family is None or family.get("id") != membership.get("id"):
        raise ValueError("Program family definition is missing or mismatched")
    validate_family(family)
    if family["institution_id"] != program["institution"]["id"]:
        raise ValueError("Family and variant must belong to the same institution")
    if not membership.get("variant_label"):
        raise ValueError("Family membership needs a concrete variant label")
    if membership.get("relationship", "unknown") not in RELATIONSHIPS:
        raise ValueError("Unknown program-family relationship")
    if membership.get("classification_kind", "unknown") not in CLASSIFICATIONS:
        raise ValueError("Unknown relationship classification basis")
    if (
        membership.get("relationship", "unknown") != "unknown"
        and membership.get("classification_kind", "unknown") == "unknown"
    ):
        raise ValueError("A stated relationship needs a classification basis")
    disciplines = membership.get("disciplines", [])
    if (
        not isinstance(disciplines, list)
        or not disciplines
        or any(not isinstance(v, str) or not v.strip() for v in disciplines)
    ):
        raise ValueError("Variant needs explicit disciplinary partners")
    source_ids = {source["id"] for source in program.get("sources", [])}

    def evidence(ids):
        if not ids or not set(ids) <= source_ids:
            raise ValueError("Family membership needs registered program evidence")

    evidence(membership.get("source_ids", []))
    for unit in membership.get("hosting_units", []):
        if not unit.get("name"):
            raise ValueError("Hosting unit needs a name")
        evidence([unit.get("source_id")])
    shared = {node["id"]: node for node in family["shared_requirements"]}
    bindings = {row["shared_id"]: row for row in membership.get("requirement_bindings", [])}
    if len(bindings) != len(membership.get("requirement_bindings", [])):
        raise ValueError("Duplicate shared requirement binding")
    local_ids = [row["id"] for row in bindings.values()]
    if len(local_ids) != len(set(local_ids)):
        raise ValueError("Shared requirements cannot bind to the same program node")
    overrides = {row["shared_id"]: row for row in membership.get("requirement_overrides", [])}
    if len(overrides) != len(membership.get("requirement_overrides", [])):
        raise ValueError("Duplicate shared requirement override")
    if not set(bindings) <= set(shared) or not set(overrides) <= set(shared):
        raise ValueError("Binding or override references an unknown shared requirement")
    for override in overrides.values():
        if override.get("operation") not in {"exclude", "replace"} or not override.get("reason"):
            raise ValueError("Shared override needs an explicit operation and reason")
        evidence([override.get("source_id")])
    courses = {course["id"]: course for course in program.get("courses", [])}
    local = {node["id"]: node for node in result.get("requirements", [])}
    if len(local) != len(result.get("requirements", [])):
        raise ValueError("Duplicate local requirement IDs")
    for node in local.values():
        for field in ("family_requirement_id", "family_source_id", "component_classification"):
            node.pop(field, None)
        node["origin"] = "variant"
        node["component"] = "other"
    expanded = []
    for sid, shared_node in shared.items():
        override = overrides.get(sid, {})
        binding = bindings.get(sid)
        if override.get("operation") == "exclude":
            if binding and binding["id"] in local:
                raise ValueError("Excluded shared requirement still exists locally")
            continue
        if not binding:
            raise ValueError("Shared requirement needs a binding or explicit exclusion")
        evidence([binding.get("source_id")])
        if override.get("operation") == "replace":
            if binding["id"] not in local:
                raise ValueError("Replacement needs a local requirement with its bound ID")
            node = local[binding["id"]]
            node.update(origin="replacement", family_requirement_id=sid)
            node.setdefault("component", "other")
            continue
        if binding["id"] in local:
            raise ValueError("Shared/local requirement collision needs an explicit replacement")
        if shared_node.get("parent_id"):
            parent_binding = bindings.get(shared_node["parent_id"])
            if not parent_binding or binding.get("parent_id") != parent_binding["id"]:
                raise ValueError(
                    "Shared parent structure cannot change without an explicit replacement"
                )
        course_ids = binding.get("course_ids", [])
        if any(cid not in courses for cid in course_ids):
            raise ValueError("Shared binding references an unknown program course")
        if sorted(courses[cid]["code"] for cid in course_ids) != sorted(
            shared_node.get("course_codes", [])
        ):
            raise ValueError("Shared binding does not match reviewed course identities")
        node = {k: deepcopy(v) for k, v in shared_node.items() if k != "course_codes"}
        node.update(
            id=binding["id"],
            parent_id=binding.get("parent_id"),
            source_id=binding["source_id"],
            course_ids=course_ids,
            origin="family",
            family_requirement_id=sid,
            family_source_id=shared_node["source_id"],
            component_classification=family["classification_kind"],
        )
        expanded.append(node)
    for node in local.values():
        node.setdefault("origin", "variant")
    result["requirements"] = list(local.values()) + expanded
    nodes = {node["id"]: node for node in result["requirements"]}
    for component in membership.get("components", []):
        if component.get("kind") not in COMPONENTS or component.get(
            "classification_kind"
        ) not in CLASSIFICATIONS - {"unknown"}:
            raise ValueError("Component annotation needs a type and classification basis")
        evidence(component.get("source_ids", []))
        for rid in component.get("requirement_ids", []):
            if rid not in nodes:
                raise ValueError("Component annotation references an unknown requirement")
            nodes[rid]["component"] = component["kind"]
            nodes[rid]["component_classification"] = component["classification_kind"]
    validate_requirements(result)
    return result
